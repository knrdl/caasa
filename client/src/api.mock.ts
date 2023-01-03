
function mockResponse(body) {
    switch (body.request) {
        case 'login':
            return `{"response": "login", "payload": {"username": "${body.payload.username}"}}`
        case 'get_system_info':
            return `{"response": "get_system_info", "payload": {"version": "20.10.7", "containers": {"total": 178, "running": 170, "stopped": 0}, "os": "Ubuntu 20.04.3 LTS", "cpus": 24, "mem": 31277850624}}`
        case 'get_container_list':
            return `{"response": "get_container_list", "payload": [
                {"id": "2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8586", "name": "CaaSa Demo", "namespace": null, "status": "running", "permissions": ["info", "info-annotations", "procs", "files-read", "files-write", "files", "logs", "state", "term"]},
                {"id": "2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8587", "name": "Backend", "namespace": "Cool Web App", "status": "running", "permissions": ["info", "info-annotations", "procs", "files-read", "files-write", "files", "logs", "state", "term"]},
                {"id": "2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8588", "name": "Gateway", "namespace": "Cool Web App", "status": "running", "permissions": ["info", "info-annotations", "procs", "files-read", "files-write", "files", "logs", "state", "term"]}
               ]}`
        case 'get_processes':
            return `{"response": "get_processes", "payload": [{"pid": "45756", "ppid": "45733", "%cpu": "0.0", "%mem": "0.0", "user": "root", "stime": "16:24", "command": "nginx: master process nginx -g daemon off;", "level": 0}, {"pid": "45822", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45823", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45824", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45825", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45826", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45827", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45828", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45829", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45830", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45831", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45832", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "45833", "ppid": "45756", "%cpu": "0.0", "%mem": "0.0", "user": "systemd+", "stime": "16:24", "command": "nginx: worker process", "level": 1}, {"pid": "46825", "ppid": "45733", "%cpu": "0.0", "%mem": "0.0", "user": "root", "stime": "16:34", "command": "sh", "level": 0}]}`
        case 'get_container_info':
            const container_name = {
                '2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8586': '/caasa_demo',
                '2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8587': '/cool_web_app_backend_1',
                '2b7eb6b9d2f7fd2dd26738500a81a16310f78e46eea2f9c2a27ed876d85d8588': '/cool_web_app_gateway_1',
            }
            return `{"response": "get_container_info", "payload": {"id": "${body.payload.container_id}", "name": "${container_name[body.payload.container_id]}", "status": "running", "command": "/docker-entrypoint.sh nginx -g daemon off;", "created_at": "2021-12-02T10:33:16.628618832Z", "started_at": "2021-12-02T10:33:17.015866729Z", "finished_at": "0001-01-01T00:00:00Z", "crashes": 0, "env": {"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "NGINX_VERSION": "1.21.1", "NJS_VERSION": "0.6.1", "PKG_RELEASE": "1"}, "labels": {"caasa.admin.full": "user1,user2", "maintainer": "NGINX Docker Maintainers <docker-maint@nginx.com>"}, "image": {"name": "nginx:alpine", "hash": "sha256:b9e2356ea1be9452f3777a587b0b6a30bc16c295fe6190eda6a0776522f27439"}, "mem": {"used": 10452992, "max_used": 19345408, "total": 52428800}, "cpu": {"perc": ${Math.random() * 10}}, "net": {"rx_bytes": 18201, "tx_bytes": 0}, "ports": ["80/tcp"]}}`
        case 'get_container_logs':
            if (body.payload.onlynew)
                return `{"response": "get_container_logs", "payload":""}`
            else
                return `{"response": "get_container_logs", "payload": "2021-12-02T10:33:17.021946340Z /docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration\\r\\n2021-12-02T10:33:17.021988550Z /docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/\\r\\n2021-12-02T10:33:17.023417432Z /docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh\\r\\n2021-12-02T10:33:17.031231257Z 10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf\\r\\n2021-12-02T10:33:17.055742664Z 10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf\\r\\n2021-12-02T10:33:17.056041305Z /docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh\\r\\n2021-12-02T10:33:17.059979717Z /docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh\\r\\n2021-12-02T10:33:17.062059371Z /docker-entrypoint.sh: Configuration complete; ready for start up\\r\\n2021-12-02T10:33:17.074027144Z 2021/12/02 10:33:17 [notice] 1#1: using the \\"epoll\\" event method\\r\\n2021-12-02T10:33:17.074056600Z 2021/12/02 10:33:17 [notice] 1#1: nginx/1.21.1\\r\\n2021-12-02T10:33:17.074063653Z 2021/12/02 10:33:17 [notice] 1#1: built by gcc 10.3.1 20210424 (Alpine 10.3.1_git20210424) \\r\\n2021-12-02T10:33:17.074069845Z 2021/12/02 10:33:17 [notice] 1#1: OS: Linux 5.11.0-40-generic\\r\\n2021-12-02T10:33:17.074075475Z 2021/12/02 10:33:17 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576\\r\\n2021-12-02T10:33:17.074245905Z 2021/12/02 10:33:17 [notice] 1#1: start worker processes\\r\\n2021-12-02T10:33:17.074276953Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 32\\r\\n2021-12-02T10:33:17.074379486Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 33\\r\\n2021-12-02T10:33:17.074401427Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 34\\r\\n2021-12-02T10:33:17.074513127Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 35\\r\\n2021-12-02T10:33:17.074601242Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 36\\r\\n2021-12-02T10:33:17.074666745Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 37\\r\\n2021-12-02T10:33:17.074817979Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 38\\r\\n2021-12-02T10:33:17.074873423Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 39\\r\\n2021-12-02T10:33:17.075007344Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 40\\r\\n2021-12-02T10:33:17.075141746Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 41\\r\\n2021-12-02T10:33:17.075279715Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 42\\r\\n2021-12-02T10:33:17.075393118Z 2021/12/02 10:33:17 [notice] 1#1: start worker process 43\\r\\n"}`
        case 'get_filesystem_info':
            return `{"response": "get_filesystem_info", "payload": {"workdir": "", "mounts": [{"type": "bind", "destination": "/etc/ssl/certs", "readonly": true, "source": "/etc/ssl/certs"}]}}`
        case 'get_directory_list':
            if (body.payload.path === '' || body.payload.path === '/')
                return `{"response": "get_directory_list", "payload": {"entries": [{"type": "f", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "0B", "modtime": "2021-12-02 16:19:13", "name": ".dockerenv"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "bin"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "360B", "modtime": "2021-12-02 16:19:13", "name": "dev"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-07-06 19:40:27", "name": "docker-entrypoint.d"}, {"type": "f", "permissions": "rwxrwxr-x", "owner": "root", "group": "root", "filesize": "1.2KB", "modtime": "2021-07-06 19:40:16", "name": "docker-entrypoint.sh"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-12-02 16:19:13", "name": "etc"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "home"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "lib"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "media"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "mnt"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "opt"}, {"type": "d", "permissions": "r-xr-xr-x", "owner": "root", "group": "root", "filesize": "0B", "modtime": "2021-12-02 16:19:13", "name": "proc"}, {"type": "d", "permissions": "rwx------", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "root"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-12-02 16:19:13", "name": "run"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "sbin"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "srv"}, {"type": "d", "permissions": "r-xr-xr-x", "owner": "root", "group": "root", "filesize": "0B", "modtime": "2021-12-02 16:19:13", "name": "sys"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "usr"}, {"type": "d", "permissions": "rwxr-xr-x", "owner": "root", "group": "root", "filesize": "4.0KB", "modtime": "2021-06-15 14:34:40", "name": "var"}], "path": "/"}}`
            else
                return false
        case 'spawn_terminal':
            return `{"response": "spawn_terminal", "payload": {"execId": "2680be7b4aa3c0b6599edf3521f5813a770ccec7966a59c57cfdac5b4e3b7e9a"}}`
        case 'resize_terminal':
            return true
        case 'transmit_terminal_input':
            if (body.payload.data === "\r")
                return `56!{"response": "receive_terminal_output", "payload": null}\r\nThis is just a demo`
            else
                return `56!{"response": "receive_terminal_output", "payload": null}` + body.payload.data
        default:
            return false
    }
}

export class WebSocketMock implements WebSocket {
    constructor(url: string) {
    }
    binaryType: BinaryType
    bufferedAmount: number
    extensions: string
    onclose: (this: WebSocket, ev: CloseEvent) => any
    onerror: (this: WebSocket, ev: Event) => any
    onmessage: (this: WebSocket, ev: MessageEvent<any>) => any
    onopen: (this: WebSocket, ev: Event) => any
    protocol: string
    readyState: number
    url: string
    close(code?: number, reason?: string): void {
    }
    CLOSED: number
    CLOSING: number
    CONNECTING: number
    OPEN: number
    addEventListener<K extends keyof WebSocketEventMap>(type: K, listener: (this: WebSocket, ev: WebSocketEventMap[K]) => any, options?: boolean | AddEventListenerOptions): void
    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void
    addEventListener(type: any, listener: any, options?: any): void {
        throw new Error("Method not implemented.")
    }
    removeEventListener<K extends keyof WebSocketEventMap>(type: K, listener: (this: WebSocket, ev: WebSocketEventMap[K]) => any, options?: boolean | EventListenerOptions): void
    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void
    removeEventListener(type: any, listener: any, options?: any): void {
        throw new Error("Method not implemented.")
    }
    dispatchEvent(event: Event): boolean {
        throw new Error("Method not implemented.")
    }

    send(requestData: string) {
        // console.log('WS>', requestData)
        const body = JSON.parse(requestData)
        const res = mockResponse(body)
        // console.log('WS<', res)
        const msg: Event & { data: string | Blob } = {
            data: undefined,
            ...new Event('api-mock')
        }
        if (res === false) {
            msg.data = `{"response": "${body.request}", "error": "Sorry, command not mocked in demo"}`
        } else if (res === true) {
            // do not send response
        } else if (res[0] !== '{') {
            console.log('send as blob', res)
            msg.data = new Blob([res])
        } else {
            msg.data = res
        }
        if (msg.data) {
            setTimeout(() => this.onmessage(msg as MessageEvent), 200)
            if (typeof msg.data === 'string' && msg.data.includes('spawn_terminal')) {
                console.log('extra response for terminal')
                const msg2: Event & { data: Blob } = {
                    data: undefined,
                    ...new Event('api-mock')
                }
                msg2.data = new Blob([`56!{"response": "receive_terminal_output", "payload": null}/ # `])
                setTimeout(() => this.onmessage(msg2 as MessageEvent), 300)
            }
        }
    }

}
