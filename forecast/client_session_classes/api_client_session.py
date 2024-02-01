import asyncio
from typing import Any

import aiohttp
from yarl import URL

from forecast.client_session_classes.extended_client_session import (
    ExtendedClientSession,
    JsonData,
)


class ApiClientSession(ExtendedClientSession):
    def __init__(
        self,
        base_url: str | URL,
        api_key: str | None,
        connector: aiohttp.BaseConnector | None = None,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(base_url, connector, loop=loop, **kwargs)

        self.api_key = api_key

    async def api_get(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='GET', **kwargs)

    async def api_post(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='POST', **kwargs)
