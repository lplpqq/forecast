import asyncio
import gc
import gzip
import json
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Literal, Self, TypeAlias

import aiohttp
from yarl import URL

from forecast.logging import logger_provider

MethodType: TypeAlias = Literal['GET', 'POST']
CompressionType: TypeAlias = Literal['gzip'] | None
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

    async def _request_json(
        self, endpoint: str, *, method: MethodType, **kwargs: Any
    ) -> JsonData:
        async with self._request_wrapper(method, endpoint, **kwargs) as response:
            raw = await response.json()

            self.logger.debug('JSON data:')
            self.logger.debug(json.dumps(raw, indent=4))

            return raw

    async def _request_file(
        self,
        endpoint: str,
        *,
        method: MethodType = 'GET',
        compression: CompressionType = None,
        **kwargs: Any,
    ) -> bytes:
        async with self._request_wrapper(method, endpoint, **kwargs) as response:
            contents = await response.read()
            self.logger.debug(f'File contents size: approx. {len(contents)} bytes')

            if compression is None:
                return contents

            match compression:
                case 'gzip':
                    decompressed = gzip.decompress(contents)

            del contents
            gc.collect(generation=0)

            return decompressed

    async def get_file(
        self,
        endpoint: str,
        *,
        compression: CompressionType = None,
        **kwargs: Any,
    ) -> bytes:
        return await self._request_file(
            endpoint, method='GET', compression=compression, **kwargs
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

    async def api_get_file(
        self,
        endpoint: str,
        *,
        compression: CompressionType = None,
        **kwargs: Any,
    ) -> bytes:
        return await self.get_file(endpoint, compression=compression, **kwargs)

    async def api_get(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='GET', **kwargs)

    async def api_post(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='POST', **kwargs)
