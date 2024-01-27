from pathlib import Path

from pydantic import BaseModel

from lib.config import BaseConfig


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


class Config(BaseConfig):
    data_sources: SourcesConfig


BASE_CONFIG_FOLDER = Path('./config/')
config_file = BASE_CONFIG_FOLDER.joinpath('./dev.yaml')

config = Config.load(config_file)
