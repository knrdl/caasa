import asyncio
import io
import os.path
import re
import tarfile
import traceback
from typing import Dict, List, Literal, Set

import aiodocker
import config
from aiodocker.containers import DockerContainer
from aiodocker.stream import Stream

client = aiodocker.Docker()


def _get_labels(container: DockerContainer) -> Dict[str, str]:
    if 'Labels' in container._container:
        return container['Labels']
    elif 'Config' in container._container:
        return container['Config'].get('Labels', {})
    else:
        return {}


def get_user_container_permissions(username: str, container: DockerContainer) -> Set[config.PermissionType]:
    username = username.lower()
    perms = set()
    try:
        labels = _get_labels(container)
        for role in config.ROLES_PERMS:
            if any((name.strip().lower() == username for name in labels.get(role, '').split(','))):  # if user has role
                perms.update(config.ROLES_PERMS[role])
    except Exception:
        traceback.print_exc()
    return perms


async def get_system_info(username: str):
    # show only system info if user has access to at least one container
    if await get_user_containers(username):
        data = await client.system.info()
        if 'BuildahVersion' in data:
            engine = 'Podman'
        else:
            engine = 'Docker'
        return {
            'engine_version': engine + ' ' + data['ServerVersion'],
            'containers': {
                'total': data['Containers'],
                'running': data['ContainersRunning'],
                'stopped': data['ContainersStopped']
            },
            'os': data['OperatingSystem'],
            'cpus': data['NCPU'],
            'mem': data['MemTotal']
        }
    else:
        raise Exception('Found no containers assigned to you.')


async def get_user_containers(username: str):
    output = []
    role_filter = [f'label={role}' for role in config.ROLES_PERMS]
    containers = await client.containers.list(filter=role_filter, all=True)
    for container in containers:
        permissions = get_user_container_permissions(username, container)
        if permissions:
            labels = container['Labels']
            namespace = labels.get('com.docker.compose.project')
            name = (labels.get('com.docker.compose.service') if namespace else container['Names'][0]).title()
            output.append({
                'id': container.id,
                'name': name.replace('-', ' ').replace('_', ' ').removeprefix('/'),
                'namespace': namespace,
                'status': container['State'],
                'permissions': list(permissions)
            })
    output.sort(key=lambda x: f"{x['namespace']} {x['name']}")
    return output


async def fetch_logs(username: str, container_id: str, since: int):
    container = await client.containers.get(container_id)
    if 'logs' in get_user_container_permissions(username, container):
        loglines = []
        async with container.docker._query(f'containers/{container_id}/logs',
                                           params={'stdout': True, 'stderr': True, 'timestamps': True,
                                                   'since': since, 'tail': 5000}) as response:
            while True:
                msg = await response.content.readline()
                if not msg:
                    break
                msg_header = msg[:8]  # first 8 bytes are usually header
                stdout, stderr = 0x01, 0x02
                if msg_header[0] in (stdout, stderr):  # message has header
                    loglines.append(msg[8:].decode('utf-8'))
                else:  # some docker versions leave the header out
                    loglines.append(msg.decode('utf-8'))
        return loglines
    else:
        raise Exception('unauthorized to access container')


async def get_container_info(username: str, container_id: str):
    container = await client.containers.get(container_id)
    permissions = get_user_container_permissions(username, container)
    if 'info' in permissions:
        running = container['State']['Status'] == 'running'
        env_vars = {}
        if 'info-annotations' in permissions:
            for env in container['Config']['Env']:
                key, value = env.split('=', 1)
                env_vars[key] = value
        else:
            env_vars = None
        if running:
            stats = await container.stats(stream=False)

            stats = stats[0]

            try:
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage'][
                    'total_usage']
                system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                online_cpus = stats['cpu_stats']['online_cpus'] or len(stats['cpu_stats']['cpu_usage']['percpu_usage'])
                cpu_perc = (cpu_delta / system_cpu_delta) * online_cpus * 100.0
            except KeyError:
                cpu_perc = None

            mem_used = mem_used_max = mem_total = None
            if 'usage' in stats['memory_stats']:
                mem_used = stats['memory_stats']['usage'] - stats['memory_stats'].get('stats', {}).get('cache', 0)
            mem_used_max = stats['memory_stats'].get('max_usage', None)
            mem_total = stats['memory_stats'].get('limit', None)

            if mem_total is not None and mem_total == mem_used_max and mem_total > 1024 ** 5:
                mem_total = mem_used_max = None

            rx_bytes = sum([v['rx_bytes'] for v in stats['networks'].values()])
            tx_bytes = sum([v['tx_bytes'] for v in stats['networks'].values()])
        else:
            cpu_perc = mem_used = mem_used_max = mem_total = rx_bytes = tx_bytes = None
        if len(container['Args']) > 0 and container['Path'] == container['Args'][0]:
            cmd = ' '.join(container['Args'])
        else:
            cmd = ' '.join([container['Path'], *container['Args']])
        return {
            'id': container.id,
            'name': container['Name'],
            'status': container['State']['Status'],
            'command': cmd.removeprefix('/bin/sh -c '),
            'created_at': container['Created'],
            'started_at': container['State']['StartedAt'],
            'finished_at': container['State']['FinishedAt'],
            'crashes': container['RestartCount'],
            'env': env_vars,
            'labels': _get_labels(container) if 'info-annotations' in permissions else None,
            'image': {
                'name': container['Config']['Image'],
                'hash': container['Image']
            },
            'mem': {'used': mem_used, 'max_used': mem_used_max, 'total': mem_total} if running else None,
            'cpu': {'perc': cpu_perc} if cpu_perc is not None else None,
            'net': {'rx_bytes': rx_bytes, 'tx_bytes': tx_bytes} if running else None,
            'ports': sorted(container['NetworkSettings']['Ports'].keys(), key=lambda p: int(p.split('/')[0]))
        }
    else:
        raise Exception('unauthorized to access container')


async def get_processes(username: str, container_id: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'procs' in get_user_container_permissions(username, container):
        try:
            data = await container.docker._query_json(
                f'containers/{container_id}/top', method='GET',
                params={'ps_args': 'ax -o pid,ppid,%cpu,%mem,user,stime,command'}
            )
        except Exception:
            data = await container.docker._query_json(
                f'containers/{container_id}/top', method='GET',
                params={'ps_args': 'ax -o pid,ppid,user,comm'}
            )
        if len(data['Titles']) == 1:
            data['Titles'] = data['Titles'][0].split()
            data['Processes'] = [p[0].split() for p in data['Processes']]
        titles = [t.lower() for t in data['Titles']]
        procs = []
        for proc in data['Processes']:
            procs.append(dict(zip(titles, proc)))
        for proc in procs:
            proc['hierarchy'] = [int(proc['pid'])]
            ppid = proc['ppid']
            while True:
                parent_process = next((p for p in procs if p['pid'] == ppid), None)
                if parent_process:
                    proc['hierarchy'].insert(0, int(parent_process['pid']))
                    ppid = parent_process['ppid']
                    if parent_process['ppid'] == parent_process['pid']:
                        break
                else:
                    break
        procs.sort(key=lambda p: proc['hierarchy'])
        for proc in procs:
            proc['level'] = len(proc['hierarchy']) - 1
            del proc['hierarchy']
        return procs
    else:
        raise Exception('unauthorized to access container')


async def set_container_state(username: str, container_id: str, state: Literal['start', 'stop', 'restart']):
    container: DockerContainer = await client.containers.get(container_id)
    if 'state' in get_user_container_permissions(username, container):
        if state == 'start':
            await container.start()
        elif state == 'stop':
            await container.stop()
        elif state == 'restart':
            await container.restart()
        else:
            raise Exception('unknown container state')
    else:
        raise Exception('unauthorized to access container')


async def get_filesystem_info(username: str, container_id: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'files' in get_user_container_permissions(username, container):
        mounts = []
        for mount in container['Mounts']:
            output = {'type': mount['Type'], 'destination': mount['Destination'], 'readonly': not mount['RW']}
            if mount['Type'] == 'volume':
                output['source'] = mount['Name']
            else:
                output['source'] = mount['Source']
            mounts.append(output)
        return {'workdir': container['Config']['WorkingDir'], 'mounts': mounts}
    else:
        raise Exception('unauthorized to access container')


def _parse_path(path: str):
    path = path or ''
    if not path.startswith('/'):
        path = '/' + path
    path = os.path.abspath(path)
    if any(path.startswith(p) for p in {'/proc', '/sys', '/dev', '/run'}):
        raise Exception('permission denied')
    return path


async def _exec_output(container: DockerContainer, cmd: List[str], timeout=10, **kwargs):
    process = await container.exec(cmd=cmd, **kwargs)
    async with process.start() as exe:
        timeout_ctr = 0
        while True:
            details = await process.inspect()
            if details['Running']:
                if timeout:
                    timeout_ctr += 1
                await asyncio.sleep(.1)
                if timeout_ctr > timeout * 10:
                    break
            else:
                break
        details = await process.inspect()
        if details['ExitCode'] != 0:
            raise Exception('error reading directory')
        msg = await exe.read_out()
    if msg:
        return msg.data.decode('utf8')


async def list_directory(username: str, container_id: str, path: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'files' in get_user_container_permissions(username, container):
        path = _parse_path(path)
        cmd = ['ls', '-1', '-A', '-h', '--full-time', '-l', path]
        output = await _exec_output(container, cmd=cmd)
        entries = []
        for entry in output.splitlines():
            m = re.search(
                r'^([a-z-])([rwx-]{9})\s+\d+\s+(\w+)\s+(\w+)\s+([\w\\.]+)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[\\.\d+]*\s+\+\d{4}\s+(.+)$',
                entry)
            if m:
                typ, permissions, owner, group, filesize, modtime, name = m.groups()
                if typ == 'l':  # link
                    name = name.split(' -> ')[0]
                entries.append(
                    {'type': typ.replace('-', 'f'), 'permissions': permissions, 'owner': owner, 'group': group,
                     'filesize': filesize + 'B', 'modtime': modtime, 'name': name})
        return {'entries': entries, 'path': path}
    else:
        raise Exception('unauthorized to access container')


async def create_folder(username: str, container_id: str, path: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'files-write' in get_user_container_permissions(username, container):
        path = _parse_path(path)
        await _exec_output(container, cmd=['mkdir', '-p', path])
        return {'path': path}
    else:
        raise Exception('unauthorized to access container')


async def upload_file(username: str, container_id: str, path: str, content: bytes):
    container: DockerContainer = await client.containers.get(container_id)
    if 'files-write' in get_user_container_permissions(username, container):
        path = _parse_path(path)
        tardata = io.BytesIO()
        with tarfile.open(fileobj=tardata, mode='w') as f:
            info = tarfile.TarInfo(os.path.basename(path))
            info.size = len(content)
            f.addfile(fileobj=io.BytesIO(content), tarinfo=info)
        tardata.seek(0)
        await container.put_archive(os.path.dirname(path), tardata)
        return {'path': path}
    else:
        raise Exception('unauthorized to access container')


async def download_file(username: str, container_id: str, path: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'files-read' in get_user_container_permissions(username, container):
        path = _parse_path(path)
        tar = await container.get_archive(path)
        for item in tar:
            if os.path.basename(path) == item.name:
                return {'path': path}, tar.extractfile(item.name).read()
    else:
        raise Exception('unauthorized to access container')


async def spawn_terminal(username: str, container_id: str, cmd: str, user: str):
    container: DockerContainer = await client.containers.get(container_id)
    if 'term' in get_user_container_permissions(username, container):
        process = await container.exec(cmd=cmd, tty=True, user=user, stdin=True)
        stream: Stream = process.start()
        return process, stream
    else:
        raise Exception('unauthorized to access container')
