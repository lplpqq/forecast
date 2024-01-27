from pathlib import Path

from lib.logging import setup_logging

TEST_LOG_FILE = Path('./test.log')
setup_logging('forecast_test', TEST_LOG_FILE)
