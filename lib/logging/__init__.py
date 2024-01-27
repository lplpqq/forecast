import logging
import logging.config
from contextvars import ContextVar
from pathlib import Path

DEFAULT_MAIN_LOGGER_NAME = 'main'
DEFAULT_LOG_FILE = Path('./runtime.log')

_main_logger_name: ContextVar[str] = ContextVar('main_logger_name')
_main_logger_name.set(DEFAULT_MAIN_LOGGER_NAME)

_log_file: ContextVar[Path] = ContextVar('log_file')
_log_file.set(DEFAULT_LOG_FILE)


class LoggerProvider:
    def __call__(self, module_name: str) -> logging.Logger:
        logger = logging.getLogger(_main_logger_name.get()).getChild(module_name)
        return logger


def setup_logging(
    main_logger_name: str = DEFAULT_MAIN_LOGGER_NAME,
    log_file: Path = DEFAULT_LOG_FILE
) -> LoggerProvider:
    _main_logger_name.set(main_logger_name)
    _log_file.set(log_file)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    main_logger = root.getChild(main_logger_name)

    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')

    file_handler.setLevel(logging.DEBUG)

    stdout_handler = logging.StreamHandler()
    stdout_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    stdout_handler.setFormatter(console_formatter)
    file_handler.setFormatter(file_formatter)

    main_logger.addHandler(file_handler)
    main_logger.addHandler(stdout_handler)

    return LoggerProvider()
