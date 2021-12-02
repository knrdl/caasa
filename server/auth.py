import aiohttp

from config import AUTH_SERVICE_URL, AUTH_API_FIELD_USERNAME, AUTH_API_FIELD_PASSWORD


async def login(username: str, password: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(AUTH_SERVICE_URL, json={AUTH_API_FIELD_USERNAME: username,
                                                        AUTH_API_FIELD_PASSWORD: password}) as response:
            if not response.ok:
                raise Exception(await response.text())
