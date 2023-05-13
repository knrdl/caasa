from typing import Optional

import aiohttp
from config import AUTH_API_FIELD_PASSWORD, AUTH_API_FIELD_USERNAME, AUTH_API_URL, WEBPROXY_AUTH_HEADER
from starlette.datastructures import State


async def auth_api_login(username: str, password: str) -> None:
    if AUTH_API_URL:
        async with aiohttp.ClientSession() as session:
            async with session.post(AUTH_API_URL, json={AUTH_API_FIELD_USERNAME: username,
                                                        AUTH_API_FIELD_PASSWORD: password}) as response:
                if not response.ok:
                    raise Exception(await response.text())
    else:
        raise Exception('auth api login is disabled')


async def webproxy_login(state: State):
    username: Optional[str] = None
    if WEBPROXY_AUTH_HEADER:
        username = state.websocket.headers.get(WEBPROXY_AUTH_HEADER, None)
        if not username:
            raise Exception(
                f'web proxy auth has been configured but the http request lacks the required header "{WEBPROXY_AUTH_HEADER}"')
    return username
