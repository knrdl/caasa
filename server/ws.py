import json
import sys

from starlette.datastructures import State
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket
from urllib.parse import urlparse

ws_actions = {}


def cmd(auth: bool):
    def wrapper(func):
        if auth:
            ws_actions[func.__name__] = _auth_required(func)
        else:
            ws_actions[func.__name__] = func
        return ws_actions[func.__name__]

    return wrapper


def _auth_required(func):
    async def inner(state: State, **params):
        if state.username:
            return await func(state, **params)
        else:
            raise Exception('auth missing')

    return inner


async def send_json_bytes(websocket: WebSocket, action: str, json_payload, binary: bytes):
    header = json.dumps({'response': action, 'payload': json_payload}).encode()
    await websocket.send_bytes(str(len(header)).encode() + b'!' + header + binary)


async def send_json(websocket: WebSocket, action: str, json_payload):
    await websocket.send_json({'response': action, 'payload': json_payload})


class WebSocketHandler(WebSocketEndpoint):
    async def on_connect(self, websocket: WebSocket):
        # check for same request origin of webclient url and websocket opener
        # (needed because websocket isn't affected by CORS)
        origin = urlparse(websocket.headers.get('origin'))
        host = websocket.url
        if origin.netloc and host.netloc and origin.netloc == host.netloc:
            if origin.scheme != 'https':
                print('Insecure HTTP request detected. Please serve the application via HTTPS.', file=sys.stderr)
            await websocket.accept()
        else:
            print('Cross-Site WebSocket Hijacking detected. '
                  'If the application is served behind a reverse-proxy, you maybe forgot to pass the host header.',
                  file=sys.stderr)
            await websocket.close()

    async def on_receive(self, websocket: WebSocket, data):
        body = json.loads(data)
        action, payload = body['request'], body.get('payload', {})
        if action in ws_actions:
            try:
                websocket.state.websocket = websocket
                response = await ws_actions[action](websocket.state, **payload)
                if response is not None:
                    if type(response) == tuple and len(response) == 2 and type(response[0]) == dict and type(
                            response[1]) == bytes:
                        payload, binary = response
                        await send_json_bytes(websocket, action, payload, binary)
                    else:
                        await send_json(websocket, action, response)
            except Exception as e:
                await websocket.send_json({'response': action, 'error': str(e)})
        else:
            await websocket.send_json({'response': action, 'error': 'unknown command'})
