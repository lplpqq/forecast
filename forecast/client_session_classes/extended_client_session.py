import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Self, TypeAlias

import aiohttp
from yarl import URL

from forecast.logging import logger_provider


JsonData: TypeAlias = dict[Any, Any]


class ExtendedClientSession(aiohttp.ClientSession):
    def __init__(
        self,
        base_url: str | URL,
        connector: aiohttp.BaseConnector | None = None,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        **kwargs: Any,
    ) -> None:
        self.logger = logger_provider(__name__)

        if not isinstance(base_url, URL):
            base_url = URL(base_url)

        self._base_path = base_url.path
        if self._base_path.endswith('/'):
            self.logger.warning(
                'The base url should not end in a slash. Removing it for you'
            )
            self._base_path = self._base_path[:-1]

        base_url.origin()
        super().__init__(
            base_url,
            connector=connector,
            loop=loop,
            connector_owner=connector is None,
            **kwargs,
        )

    async def __aenter__(self) -> Self:
        return self

    def _resolve_relative_path(self, additional: str) -> str:
        additional = additional if additional.startswith('/') else f'/{additional}'
        return self._base_path + additional

    @asynccontextmanager
    async def _request_wrapper(
        self, method: str, relative_endpoint: str, **kwargs: Any
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        endpoint_path_from_base = self._resolve_relative_path(relative_endpoint)

        full_url = self._base_path + endpoint_path_from_base
        self.logger.info(f'Sending a {method} request to "{full_url}"')

        start = time.perf_counter()
        async with self.request(method, endpoint_path_from_base, **kwargs) as response:
            end = time.perf_counter()
            total_time_ms = (end - start) * 1000

            self.logger.info(
                f'[Time taken - {total_time_ms:.2f} ms] Got response from "{full_url}", status: {response.status}'
            )

            response.raise_for_status()
            yield response

    async def get_json(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> JsonData:
        async with self._request_wrapper('GET', endpoint, **kwargs) as response:
            raw = await response.json()
            return raw

    async def get_raw(
        self,
        endpoint: str,
        **kwargs: Any,
    ) -> bytes:
        async with self._request_wrapper('GET', endpoint, **kwargs) as response:
            content = await response.read()
            self.logger.debug(f'File contents size: approx. {len(content)} bytes')
            return content
