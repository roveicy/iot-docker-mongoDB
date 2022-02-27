import yaml
import logging
from dockers.IoT.src.sensor_factory import SensorFactory
from src.sensors import ASDSensor, GPSSensor
import pathlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

ASSETS_PATH = pathlib.Path('./assets')


def load_assets() -> None:
    GPSSensor.load_assets(ASSETS_PATH / 'gps_path.txt')
    ASDSensor.load_assets(ASSETS_PATH / 'asd.wav')


def main() -> None:
    load_assets()

    with open('config/config.yaml', 'r') as config_file:
        total_config:dict = yaml.load(config_file, Loader=yaml.SafeLoader)
    assert total_config.get('sensors'), 'config file should contain sensors configurations with "sensors" as key'
    sensor_factory: SensorFactory = SensorFactory(total_config.get('sensors'))
    # todo: load schedule

if __name__ == '__main__':
    main()