from pathlib import Path

from pydantic import BaseModel

from lib.config import BaseConfig


class WeatherBitSourceConfig(BaseModel):
    api_key: str


class SourcesConfig(BaseModel):
    weatherbit: WeatherBitSourceConfig


class Config(BaseConfig):
    data_sources: SourcesConfig


BASE_CONFIG_FOLDER = Path('./config/')
config_file = BASE_CONFIG_FOLDER.joinpath('./dev.yaml')

config = Config.load(config_file)
