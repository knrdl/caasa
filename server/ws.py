import json
import traceback
from typing import Any, Awaitable, Callable
from urllib.parse import urlparse

from logger import logger
from starlette.datastructures import State
from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket

AsyncFuncType = FuncType = Callable[[Any], Awaitable[Any]]

_ws_actions: dict[str, AsyncFuncType] = {}
_ws_on_connect_handler: list[AsyncFuncType] = []


def on_connect():
    def wrapper(func: AsyncFuncType):
        _ws_on_connect_handler.append(func)

    return wrapper


def cmd(auth: bool):
    def wrapper(func):
        if auth:
            _ws_actions[func.__name__] = _auth_required(func)
        else:
            _ws_actions[func.__name__] = func
        return _ws_actions[func.__name__]

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
                logger.warning('Insecure HTTP request detected. Please serve the application via HTTPS.')
            await websocket.accept()
            await self.after_connect(websocket)
        else:
            logger.warning('Cross-Site WebSocket Hijacking detected. '
                           'If the application is served behind a reverse-proxy, you maybe forgot to pass the host header.')
            await websocket.close()

    async def after_connect(self, websocket: WebSocket):
        websocket.state.websocket = websocket
        for handler in _ws_on_connect_handler:
            try:
                result = await handler(websocket.state)
                if isinstance(result, tuple) and len(result) == 2:
                    action, response = result
                    await send_json(websocket, action, response)
                elif result is not None:
                    raise Exception('invalid response format for on_connect handler')
            except Exception as e:
                traceback.print_exc()
                await websocket.send_json({'response': 'connection_init', 'error': str(e)})

    async def on_receive(self, websocket: WebSocket, data: str):
        body = json.loads(data)
        action, payload = body['request'], body.get('payload', {})
        if action in _ws_actions:
            try:
                response = await _ws_actions[action](websocket.state, **payload)
                if response is not None:
                    if isinstance(response, tuple) and len(response) == 2 and \
                            isinstance(response[0], dict) and isinstance(response[1], bytes):
                        payload, binary = response
                        await send_json_bytes(websocket, action, payload, binary)
                    else:
                        await send_json(websocket, action, response)
            except Exception as e:
                traceback.print_exc()
                await websocket.send_json({'response': action, 'error': str(e)})
        else:
            await websocket.send_json({'response': action, 'error': 'unknown command'})
