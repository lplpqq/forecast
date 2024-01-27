from pathlib import Path

from pydantic import BaseModel

from forecast.logging import logger_provider
from forecast.utils.format_path import format_path
from lib.config import BaseConfig

logger = logger_provider(__name__)


class BaseDataSourceConfig(BaseModel):
    api_key: str


class WeatherBitSourceConfig(BaseDataSourceConfig):
    ...


class OpenWeartherMapSourceConfig(BaseDataSourceConfig):
    ...


class VisualCrossingSourceConfig(BaseDataSourceConfig):
    ...


class SourcesConfig(BaseModel):
    weather_bit: WeatherBitSourceConfig
    open_weather_map: OpenWeartherMapSourceConfig
    visual_crossing: VisualCrossingSourceConfig


class DBConfig(BaseModel):
    connection_string: str


class Config(BaseConfig):
    data_sources: SourcesConfig
    db: DBConfig


BASE_CONFIG_FOLDER = Path('./config/')
config_file = BASE_CONFIG_FOLDER.joinpath('./dev.yaml')

logger.info(f'Loading config from "{format_path(config_file)}"')

config = Config.load(config_file)
