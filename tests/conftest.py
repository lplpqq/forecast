from asyncio import AbstractEventLoop
from pathlib import Path

import pytest
from aiohttp import TCPConnector

from lib.logging import setup_logging

TEST_LOG_FILE = Path('./test.log')
setup_logging('forecast_test', TEST_LOG_FILE)


@pytest.fixture(params=["asyncio"])
@pytest.mark.asyncio
async def connector() -> TCPConnector:
    return TCPConnector(limit=10)
