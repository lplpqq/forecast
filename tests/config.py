import shutil

from forecast.config import BASE_CONFIG_FOLDER, Config
from forecast.config import config_file as dev_config_file

config_file = BASE_CONFIG_FOLDER.joinpath('./test.yaml')

# NOTE: Make sure to remove this in case we will want the dev and test configs to differ
if not config_file.exists():
    shutil.copy(dev_config_file, config_file)
else:
    with open(config_file) as test_config:
        with open(dev_config_file) as dev_config:
            if test_config.read() != dev_config.read():
                config_file.unlink()
                shutil.copy(dev_config_file, config_file)


config = Config.load(config_file)
