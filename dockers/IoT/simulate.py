import yaml
import logging
from src.sensors import ASDSensor, GPSSensor
import pathlib

ASSETS_PATH = pathlib.Path('./assets')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

if __name__ == '__main__':
    with open('config/config.yaml', 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
        print(config)

    GPSSensor.load_assets(ASSETS_PATH / 'gps_path.txt')
    ASDSensor.load_assets(ASSETS_PATH / 'asd.wav')
