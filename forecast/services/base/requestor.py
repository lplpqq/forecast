from abc import ABC
from types import TracebackType
from typing import Any, Self

import aiohttp
from aiohttp import ClientSession

from forecast.logging import logger_provider


class Requestor(ABC):
    def __init__(
        self, api_key: str, base_endpoint_url: str,
        conn: aiohttp.TCPConnector
    ) -> None:
        self.logger = logger_provider(__name__)

        self.api_key = api_key
        self.base_endpoint_url = base_endpoint_url

        self._connector = conn
        self._session: ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = ClientSession(connector=self._connector)

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType
    ) -> None:
        if self._session is None:
            return

        await self._session.close()

    async def _request(
        self,
        path: str,
        *,
        method: str,
        **kwargs: Any
    ) -> dict[Any, Any]:
        if self._session is None:
            raise RuntimeError('Session is not established')

        if not path.startswith('https://'):
            path = self.base_endpoint_url + path

        async with self._session.request(method, path, **kwargs) as response:
            return await response.json()

    async def _get(self, path: str, **kwargs: Any) -> dict[Any, Any]:
        return await self._request(path, method='GET', **kwargs)

    async def _post(self, path: str, **kwargs: Any) -> dict[Any, Any]:
        return await self._request(path, method='POST', **kwargs)
