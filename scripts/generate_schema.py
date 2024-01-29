import asyncio
import importlib.util
import inspect
import os
import os.path
import re
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Final, TypeAlias

import aiohttp
import orjson
import uvloop
from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    PythonVersion,
    generate,
)
from pydantic_extra_types.coordinate import Coordinate, Latitude, Longitude

from forecast.config import Config
from forecast.enums.resolution import Granularity
from forecast.providers.base import Provider
from forecast.providers.base.provider import HistoricalWeather
from lib.fs_utils import validate_path
from lib.logging import setup_logging

logger_provider = setup_logging('generate_schema', Path('./tools.log'))
logger = logger_provider(__name__)

DEFAULT_PROVIDERS_DIR: Final[Path] = Path('./forecast/providers/')
DEFAULT_OUT_DIR: Final[Path] = DEFAULT_PROVIDERS_DIR.joinpath('./schema')
DEFAULT_CONFIG_PATH: Final[Path] = Path('./config/dev.yaml')


class ToolNamespace(Namespace):
    providers_dir: Path
    out_dir: Path
    recursive: bool
    skip_on_conflict: bool
    config_path: Path


def parse_args() -> ToolNamespace:
    p = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    p.add_argument(
        'providers_dir',
        help='Directory containg all of the providers',
        type=Path,
        default=DEFAULT_PROVIDERS_DIR,
        nargs='?',
    )

    p.add_argument(
        'out_dir',
        help='Directory to output generated schemas',
        type=Path,
        default=DEFAULT_OUT_DIR,
        nargs='?',
    )

    p.add_argument(
        '--recursive',
        help='Weather to look for modules containing providers in the providers_dir recursively',
        action='store_true',
    )

    p.add_argument(
        '--skip-on-conflict',
        help='Preserve the previous schema files from out_dir, confliciting with the codgen if there are any',
        action='store_true',
    )

    p.add_argument(
        '--config',
        dest='config_path',
        help='Path to a config file containing all the api_keys, has to look the same as the Config in the forecast.config',
        required=False,
        type=Path,
        default=DEFAULT_CONFIG_PATH,
    )

    np = ToolNamespace()
    p.parse_args(namespace=np)

    validate_path(np.providers_dir, 'folder', {'readable'})
    validate_path(np.config_path, 'file', {'readable'})
    validate_path(np.out_dir, 'folder', {'readable', 'writable'}, autocreate_self=True)

    return np


def import_from_path(module_path: Path, new_module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(new_module_name, module_path)
    if spec is None:
        raise ValueError(
            f'Could not get spec from file location for module "{new_module_name}" at "{module_path}"'
        )

    module = importlib.util.module_from_spec(spec)

    logger.info(f'Adding {module.__name__} to sys.modules')
    sys.modules[module.__name__] = module

    if spec.loader is None:
        raise ValueError(
            f'spec.loader for the module at "{module_path}" happened to be None'
        )

    spec.loader.exec_module(module)

    return module


def extract_providers(from_dir: Path, recursive: bool = False) -> list[type[Provider]]:
    wanted_providers: list[type[Provider]] = []
    present_provider_names: set[str] = set()

    glob_string = './**/*.py' if recursive else './*.py'
    for module_path in from_dir.glob(glob_string):
        try:
            cwd = Path('./')
            relative_to_cwd = module_path.relative_to(cwd).resolve()
            path_parts = os.path.splitext(relative_to_cwd)
            module_name = os.path.relpath(path_parts[0], cwd).replace(os.sep, '.')

            if module_name in sys.modules:
                continue

            module = import_from_path(module_path, module_name)
            for _, value in inspect.getmembers(module, inspect.isclass):
                if (
                    not issubclass(value, Provider)
                    or value is Provider
                    or value.__name__ in present_provider_names
                ):
                    continue

                wanted_providers.append(value)
                present_provider_names.add(value.__name__)
        except ValueError as e:
            logger.error(e)
            continue

    logger.info(
        f'Discovered {len(wanted_providers)} provider(s): {", ".join(map(lambda class_: class_.__name__, wanted_providers))}'
    )
    return wanted_providers


def pascal_case_split(identifier: str) -> list[str]:
    matches = re.finditer(
        '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier
    )
    return [m.group(0) for m in matches]


def pascal_case_to_snake_case(identifier: str) -> str:
    return '_'.join(map(str.lower, pascal_case_split(identifier)))


@asynccontextmanager
async def orchestrate_providers(
    connector: aiohttp.BaseConnector,
    providers: list[Provider],
) -> AsyncIterator[list[Provider]]:
    await asyncio.gather(*[provider.setup() for provider in providers])

    try:
        yield providers
    finally:
        await asyncio.gather(*[provider.clean_up() for provider in providers])
        await connector.close()


FetchTask: TypeAlias = asyncio.Task[HistoricalWeather | None]


async def fetch_task_func(provider: Provider) -> HistoricalWeather | None:
    if not provider.is_setup:
        await provider.setup()

    result = await provider.get_historical_weather(
        Granularity.HOUR,
        Coordinate(latitude=Latitude(35.6897), longitude=Longitude(139.6922)),
        start_date=datetime(2024, 1, 5),
        end_date=datetime(2024, 1, 15),
    )

    return result


async def main(event_loop: asyncio.AbstractEventLoop) -> None:
    args = parse_args()

    config = Config.load(args.config_path)
    provider_classes = extract_providers(args.providers_dir, args.recursive)

    providers: list[Provider] = []
    connector = aiohttp.TCPConnector(limit=10)

    data_sources_config_dict = config.data_sources.model_dump()
    for provider_class in provider_classes:
        config_datasource_name = pascal_case_to_snake_case(provider_class.__name__)

        datasource_config = data_sources_config_dict.get(config_datasource_name, None)
        if datasource_config is None:
            logger.warning(
                f'{config_datasource_name} config field at "data_sources" doesn\'t exist, skipping provider: {provider_class.__name__}'
            )
            continue

        api_key_from_config = datasource_config['api_key']
        instance_ = provider_class(connector, api_key_from_config)

        providers.append(instance_)

    def log_could_not_get(name: str, e: BaseException | None = None) -> None:
        if e is not None:
            additional_error_info = 'See the error:'
        else:
            additional_error_info = 'No error provided...'

        logger.error(
            f'Could not get historic data from {name}, skipping scheme generation for it. {additional_error_info}'
        )

        if e is not None:
            logger.error(e)

    provider_names: list[str] = []
    async with orchestrate_providers(connector, providers) as providers:
        fetch_tasks: list[FetchTask] = []
        for provider in providers:
            fetch_task: FetchTask | None = None
            try:
                fetch_task = event_loop.create_task(fetch_task_func(provider))

                fetch_tasks.append(fetch_task)
                provider_names.append(provider.__class__.__name__)
            except Exception as e:
                if fetch_task is not None:
                    fetch_task.set_result(None)

                log_could_not_get(provider.__class__.__name__, e)

                continue

        done = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        all_results: dict[str, HistoricalWeather] = {}
        for data_or_exc, provider_name in zip(done, provider_names):
            try:
                if isinstance(data_or_exc, BaseException):
                    log_could_not_get(provider_name, data_or_exc)

                    continue

                if data_or_exc is None:
                    log_could_not_get(provider_name)
                    continue

                all_results[provider_name] = data_or_exc
            except Exception as e:
                # It seesms that the variable is changed by the time the iterpreter gets here. I don't really know
                log_could_not_get('<unknown>', e)

                continue

        logger.info('Preparing to generate schema from {}')
        for provider_name, data in all_results.items():
            if not isinstance(data, dict):
                logger.info(
                    f'Data from provider {provider_name} is of type {type(data)} and not a dictionary resembling json, skipping the codegen for the provider.'
                )
                continue

            module_name = pascal_case_to_snake_case(provider_name)
            out_file = args.out_dir.joinpath(module_name).with_suffix('.py')

            if out_file.exists():
                if args.skip_on_conflict:
                    logger.info(
                        f'File in the out_dir for provider "{provider_name}" already exists, skipping codegen for it. File: "{out_file}"'
                    )
                    continue
                else:
                    logger.info(
                        f'Deleting already present scheme file "{out_file}", to skip provide --skip-on-conflict'
                    )
                    out_file.unlink()

            json_string = orjson.dumps(data).decode('utf-8')
            generate(
                json_string,
                class_name=f'{provider_name}Schema',
                input_file_type=InputFileType.Json,
                target_python_version=PythonVersion.PY_311,
                output=out_file,
                snake_case_field=True,
                output_model_type=DataModelType.PydanticV2BaseModel,
            )

            logger.info(f'Generated model for "{provider_name}", save to "{out_file}"')


if __name__ == '__main__':
    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        loop = runner.get_loop()
        runner.run(main(loop))
