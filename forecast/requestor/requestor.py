import gc
import gzip
import json
from abc import ABC
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from types import TracebackType
from typing import Any, Literal, Self, TypeAlias
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientResponse, ClientSession

from forecast.logging import logger_provider

MethodType: TypeAlias = Literal['GET', 'POST']
CompressionType: TypeAlias = Literal['gzip'] | None
JsonData: TypeAlias = dict[Any, Any]



class Requestor:
    def __init__(
        self,
        base_url: str,
        conn: aiohttp.BaseConnector,
        api_key: str | None = None,
    ) -> None:
        self.logger = logger_provider(__name__)

        self.api_key = api_key

        parsed = urlparse(base_url)
        self._base_url = parsed.scheme + '://' + parsed.netloc
        self._base_endpoint = parsed.path

        if self._base_endpoint.endswith('/'):
            self._base_endpoint = self._base_endpoint[:-1]

        self._connector = conn

        self._session: ClientSession | None = None

    # note we do not need to set it up as we pass connector, which means we got to close connector from where we passed it, not ClientSession from here

    # async def __aenter__(self) -> Self:
    #     await self.setup()
    #     return self
    #
    # async def __aexit__(
    #     self,
    #     exc_type: type[BaseException],
    #     exc_value: BaseException,
    #     traceback: TracebackType,
    # ) -> None:
    #     await self.clean_up()
    #
    # async def setup(self) -> None:
    #     if self.is_setup:
    #         self.logger.warning(
    #             'Requestor is already setup, no need to class .setup() twice.'
    #         )
    #         return
    #
    #     self._session = ClientSession(
    #         connector=self._connector, base_url=self._base_url
    #     )
    #     self.is_setup = True
    #
    # async def clean_up(self) -> None:
    #     if self._session is None:
    #         self.logger.warning('You may not disconnect before even connecting.')
    #         return
    #     self.is_setup = False



    def _resolve_endpoint(self, to_add_to_base: str) -> str:
        if not to_add_to_base.startswith('/'):
            to_add_to_base = f'/{to_add_to_base}'

        return self._base_endpoint + to_add_to_base

    @asynccontextmanager
    async def _request(
        self, method: str, endpoint: str, **kwargs: Any
    ) -> AsyncIterator[ClientResponse]:
        if self._session is None:
            self._session = ClientSession(connector=self._connector, base_url=self._base_url)
            # raise RuntimeError('Session is not established')

        endpoint_path_from_base = self._resolve_endpoint(endpoint)
        full_url = self._base_url + endpoint_path_from_base

        self.logger.info(f'Sending a {method} request to "{full_url}"')
        start_time = datetime.now()

        async with self._session.request(
            method, endpoint_path_from_base, **kwargs
        ) as response:
            end_time = datetime.now()
            self.logger.info(
                f'[Time taken - {end_time - start_time}] Got response from "{full_url}", status: {response.status}'
            )

            response.raise_for_status()

            yield response

    async def _request_json(
        self, endpoint: str, *, method: MethodType, **kwargs: Any
    ) -> JsonData:
        async with self._request(method, endpoint, **kwargs) as response:
            raw = await response.json()

            self.logger.debug('JSON data:')
            self.logger.debug(json.dumps(raw, indent=4))

            return raw

    # NOTE: Option for streaming the file in chunks? In that case the compression has to be None or, as far as, I am concered the function calls to gzip or other decompresser is going to be expresive for small chunks... The whole overloading hustle as well as runtime checks.. YAGNI
    async def _request_file(
        self,
        endpoint: str,
        *,
        method: MethodType = 'GET',
        compression: CompressionType = None,
        **kwargs: Any,
    ) -> bytes:
        async with self._request(method, endpoint, **kwargs) as response:
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
        return await self._request_file(endpoint, method='GET', compression=compression, **kwargs)

    async def get(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='GET', **kwargs)

    async def post(self, path: str, **kwargs: Any) -> JsonData:
        return await self._request_json(path, method='POST', **kwargs)
