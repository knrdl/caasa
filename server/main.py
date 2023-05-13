import asyncio
import base64
import time
import traceback
from typing import Literal

import auth
import docker
import ws
from aiodocker.execs import Exec
from aiodocker.stream import Message
from starlette.applications import Starlette
from starlette.datastructures import State
from starlette.routing import Mount, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocketState


@ws.on_connect()
async def webproxy_auth(state: State):
    username = await auth.webproxy_login(state)
    if username:
        state.username = username.lower()
        return 'webproxy_auth', {'username': state.username}


@ws.cmd(auth=False)
async def login(state: State, username: str, password: str):
    await auth.auth_api_login(username, password)
    state.username = username.lower()
    return {'username': state.username}


@ws.cmd(auth=True)
async def get_system_info(state: State):
    return await docker.get_system_info(state.username)


@ws.cmd(auth=True)
async def get_container_list(state: State):
    return await docker.get_user_containers(state.username)


@ws.cmd(auth=True)
async def get_container_logs(state: State, container_id: str, onlynew: bool = False):
    if not hasattr(state, 'logs'):
        state.logs = {}
    if container_id not in state.logs:
        state.logs[container_id] = 1
    since = state.logs[container_id]
    state.logs[container_id] = int(time.time())
    return await docker.fetch_logs(state.username, container_id, since if onlynew else 1)


@ws.cmd(auth=True)
async def get_container_info(state: State, container_id: str):
    return await docker.get_container_info(state.username, container_id)


@ws.cmd(auth=True)
async def set_container_state(state: State, container_id: str, action: Literal['start', 'stop', 'restart']):
    await docker.set_container_state(state.username, container_id, action)
    return {'container_id': container_id, 'action': action}


@ws.cmd(auth=True)
async def get_processes(state: State, container_id: str):
    return await docker.get_processes(state.username, container_id)


@ws.cmd(auth=True)
async def get_filesystem_info(state: State, container_id: str):
    return await docker.get_filesystem_info(state.username, container_id)


@ws.cmd(auth=True)
async def get_directory_list(state: State, container_id: str, path: str):
    return await docker.list_directory(state.username, container_id, path)


@ws.cmd(auth=True)
async def download_file(state: State, container_id: str, path: str):
    return await docker.download_file(state.username, container_id, path)


@ws.cmd(auth=True)
async def create_folder(state: State, container_id: str, path: str):
    return await docker.create_folder(state.username, container_id, path)


@ws.cmd(auth=True)
async def upload_file(state: State, container_id: str, path: str, content: str):
    content = base64.b64decode(content)
    return await docker.upload_file(state.username, container_id, path, content)


async def _listen_for_terminal_output(state: State):
    async def close_terminal_notify():
        await close_terminal(state)
        await ws.send_json(state.websocket, 'close_terminal', {'is_closed': True})

    while hasattr(state, 'term') and state.term:
        process, stream = state.term
        if state.websocket.client_state != WebSocketState.CONNECTED:
            await close_terminal_notify()
            break
        output: Message = await stream.read_out()
        if output:
            await ws.send_json_bytes(state.websocket, 'receive_terminal_output', json_payload=None, binary=output.data)
        else:
            await close_terminal_notify()
            break


@ws.cmd(auth=True)
async def spawn_terminal(state: State, container_id: str, cmd: str, user: str):
    process, stream = await docker.spawn_terminal(state.username, container_id, cmd, user)
    try:
        await close_terminal(state)
    except BaseException:
        traceback.print_exc()
    state.term = process, stream
    asyncio.create_task(_listen_for_terminal_output(state))
    return {'execId': process.id}


@ws.cmd(auth=True)
async def close_terminal(state: State):
    if hasattr(state, 'term') and state.term:
        process, stream = state.term
        state.term = None
        await stream.close()
    return {'is_closed': True}


@ws.cmd(auth=True)
async def transmit_terminal_input(state: State, data: str):
    if hasattr(state, 'term') and state.term:
        process, stream = state.term
        await stream.write_in(data.encode())
    else:
        raise Exception('no terminal open')


@ws.cmd(auth=True)
async def resize_terminal(state: State, rows: int, cols: int):
    if hasattr(state, 'term') and state.term:
        process, stream = state.term
        process: Exec = process
        await process.resize(w=cols, h=rows)
    else:
        raise Exception('no terminal open')


app = Starlette(debug=False, routes=[
    WebSocketRoute('/ws', ws.WebSocketHandler),
    Mount('/', app=StaticFiles(directory='/www', html=True)),
])
