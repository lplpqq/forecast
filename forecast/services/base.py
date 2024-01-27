from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Literal

from aiohttp import ClientSession
from pydantic_extra_types.coordinate import Coordinate

from forecast.logging import logger_provider


class Requestor(ABC):
    def __init__(
        self, api_key: str, base_endpoint_url: str, session: ClientSession
    ) -> None:
        self.logger = logger_provider(__name__)

        self.api_key = api_key
        self.base_endpoint_url = base_endpoint_url
        self.session = session

    async def _request(self, path: str, *, method: str, **kwargs: Any) -> str:
        if not path.startswith('https://'):
            path = self.base_endpoint_url + path

        self.logger.info(f'Sending a {method} request to "{path}"')
        async with self.session.request(method, path, **kwargs) as response:
            return await response.text()

    async def _get(self, path: str, **kwargs: Any) -> str:
        return await self._request(path, method='GET', **kwargs)

    async def _post(self, path: str, **kwargs: Any) -> str:
        return await self._request(path, method='POST', **kwargs)

    @abstractmethod
    async def get_historical_weather(
        self,
        granularity: Literal['hourly', 'daily'],
        coordinate: Coordinate,
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        ...
