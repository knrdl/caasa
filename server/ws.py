import json

from starlette.datastructures import State
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

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
