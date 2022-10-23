// MOCK_PLACEHOLDER
// see .github/workflows/github-page.yml

let ws: WebSocket

type ApiRequest =
    'login'
    | 'webproxy_auth'
    | 'get_system_info'
    | 'get_container_list'
    | 'get_container_info'
    | 'get_container_logs'
    | 'set_container_state'
    | 'get_processes'
    | 'spawn_terminal'
    | 'close_terminal'
    | 'receive_terminal_output'
    | 'transmit_terminal_input'
    | 'resize_terminal'
    | 'get_filesystem_info'
    | 'get_directory_list'
    | 'download_file'
    | 'create_folder'
    | 'upload_file'
type ApiResponse = ApiRequest | 'ws-error' | 'ws-close'

let callbacksSuccess: { [key: string]: (data: any) => void } = {}
let callbacksFailure: { [key: string]: (data: any) => void } = {}

function propagateSuccessResponse(event: ApiResponse, payload: any) {
    if (event in callbacksSuccess) {
        callbacksSuccess[event](payload)
    } else {
        console.error('WS-API Unknown websocket event:', event)
    }
}

function propagateErrorResponse(event: ApiResponse, error: string) {
    if (event in callbacksFailure) {
        callbacksFailure[event](error)
    } else {
        console.error('WS-API Unknown websocket event:', event)
    }
}

function unregisterAll() {
    callbacksSuccess = {}
    callbacksFailure = {}
}


export default {
    /**
     * Init a websocket connection to the api, any old connection will be destroyed
     */
    init() {
        try {
            if (ws) {
                ws.close(1000)
            }
            ws = new WebSocket(`${window.location.protocol.replace('http', 'ws')}//${window.location.host}/ws`)
            ws.binaryType = 'blob'
            ws.onclose = (ev: CloseEvent) => {
                propagateErrorResponse('ws-close', ev.reason || 'Connection closed')
                unregisterAll()
            }
            ws.onmessage = async (ev: MessageEvent) => {
                if (ev.data instanceof Blob) {
                    const headerSize = parseInt(await ev.data.slice(0, 10).text())
                    const headerIndicatorSize = headerSize.toString().length + 1
                    const header = await ev.data.slice(headerIndicatorSize, headerIndicatorSize + headerSize).text()
                    const d = JSON.parse(header)
                    if (d.error)
                        propagateErrorResponse(d.response, d.error)
                    else
                        propagateSuccessResponse(d.response, {
                            payload: d.payload,
                            blob: ev.data.slice(headerIndicatorSize + headerSize)
                        })
                } else {
                    const d = JSON.parse(ev.data)
                    if (d.error)
                        propagateErrorResponse(d.response, d.error)
                    else
                        propagateSuccessResponse(d.response, d.payload)
                }
            }
            ws.onerror = (ev: Event) => {
                propagateErrorResponse('ws-error', 'Connection error')
            }
        } catch (e) {
            alert(e)
        }
    },

    /**
     * Register a callback to listen to events sent by websockets api
     * @param event name of the event
     * @param success Callback function
     * @param failure Callback function
     */
    register<T = void>(event: ApiResponse, success?: (data: T) => void, failure?: (err: string) => void) {
        if (success)
            callbacksSuccess[event] = success
        if (failure)
            callbacksFailure[event] = failure
    },

    /**
     * Unregister a callback to stop listening to events sent by websockets api
     * @param events names of the events
     */
    unregister(...events: ApiResponse[]) {
        events.forEach(event => {
            delete callbacksFailure[event]
            delete callbacksSuccess[event]
        })
    },

    /**
     * Send a action to the websockets api
     * @param request name of the action
     * @param payload any json serializable object
     */
    send(request: ApiRequest, payload?: any) {
        ws.send(JSON.stringify({request, payload}))
    },

    close() {
        unregisterAll()
        ws.close()
    }
}
