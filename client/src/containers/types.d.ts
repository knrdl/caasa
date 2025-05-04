type ContainerStatus = 'created' | 'restarting' | 'running' | 'removing' | 'paused' | 'exited' | 'dead'
type Tab = 'info' | 'logs' | 'term' | 'procs' | 'files'
type PermissionType =
    'info'
    | 'info-annotations'
    | 'state'
    | 'logs'
    | 'term'
    | 'procs'
    | 'files'
    | 'files-read'
    | 'files-write'

class ContainerInfoShort {
    id: string
    name: string
    namespace: string
    status: ContainerStatus
    permissions: PermissionType[]
}

class ContainerInfoLong {
    id: string
    name: string
    status: ContainerStatus
    command: string
    created_at: string
    started_at: string
    finished_at: string
    crashes: number
    'image': {
        'name': string
        'hash': string
    }
    'mem': {
        'used': number | null
        'max_used': number | null
        'total': number | null
    } | null
    'cpu': {
        'perc': number
    } | null
    'net': {
        'rx_bytes': number
        'tx_bytes': number
    } | null
    ports: string[]
    env: { [key: string]: string }
    labels: { [key: string]: string }
}

class FilesystemInfo {
    workdir: string
    mounts: { source: string, destination: string, type: string, readonly: boolean }[]
}

class DirectoryListing {
    'type': string
    'permissions': string
    'owner': string
    'group': string
    'filesize': string
    'modtime': string
    'name': string
}

class SysInfo {
    engine_version: string
    containers: {
        total: number
        running: number
        stopped: number
    }
    os: string
    cpus: number
    mem: number
}

class Proc {
    pid: string
    '%cpu': string
    '%mem': string
    stime: string
    user: string
    command: string
    level: string
}
