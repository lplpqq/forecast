from abc import ABC
from typing import Optional

from aiohttp import ClientSession

from forecast.logging import logger_provider


class Requestor(ABC):
    def __init__(
        self, base_endpoint_url: str, session: ClientSession, api_key: Optional[str] = None
    ) -> None:
        self.logger = logger_provider(__name__)

        self.base_endpoint_url = base_endpoint_url
        self.session = session
        self.api_key = api_key

    async def _request(
            self,
            path: str,
            *,
            method: str,
            **kwargs
    ):
        if not path.startswith("https://"):
            path = self.base_endpoint_url + path

        async with self.session.request(method, path, **kwargs) as response:
            return await response.text()

    async def _get(self, path: str, **kwargs):
        return await self._request(path, method="GET", **kwargs)

    async def _post(self, path: str, **kwargs):
        return await self._request(path, method="POST", **kwargs)
