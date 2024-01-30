import time
from abc import ABC, abstractmethod

from forecast.logging import logger_provider


class BaseService(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.logger = logger_provider(__name__)

        self.is_setup = False
        self.was_torn_down = False

        self.name = self.__class__.__name__

    async def setup(self) -> None:
        if self.was_torn_down:
            self.logger.warning(
                f'{self.name} service has already been torn down. You may not set it up again'
            )
            return

        if self.is_setup:
            self.logger.warning(
                f'{self.name} service has already been setup, no need to call the setup method again'
            )
            return

        self.is_setup = True
        self.logger.info(f'Finised setting up {self.name} service')

    @abstractmethod
    async def _run(self) -> None:
        ...

    async def run(self) -> None:
        if not self.is_setup or self.was_torn_down:
            self.logger.info(
                f'{self.name} service was either already been turn down or has not yet been setup. You may not run it'
            )

        self.logger.info(f'Running {self.name} service')

        # TODO: Try to make DRY, the same code is in forecast.client_session_classes.extended_client_session
        start = time.perf_counter()
        await self._run()
        end = time.perf_counter()

        total_time_ms = (end - start) * 1000
        self.logger.info(
            f'[Time taken - {total_time_ms:.2f} ms] to run {self.name} service'
        )

    async def teardown(self) -> None:
        if not self.is_setup:
            self.logger.warning(
                f'{self.name} service was never setup in the first place'
            )
            return

        if self.was_torn_down:
            self.logger.warning(
                f'{self.name} service has already been torn down, no need to call the teardown twice'
            )
            return

        self.was_torn_down = True
