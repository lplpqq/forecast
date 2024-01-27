import shutil

from forecast.config import BASE_CONFIG_FOLDER, Config
from forecast.config import config_file as dev_config_file

config_file = BASE_CONFIG_FOLDER.joinpath('./test.yaml')

if not config_file.exists():
    shutil.copy(dev_config_file, config_file)

config = Config.load(config_file)
