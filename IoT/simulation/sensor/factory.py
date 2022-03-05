from queue import SimpleQueue
import typing
import pathlib

from .device import DeviceSensor
from .camera import CameraSensor
from .gps import GPSSensor
from .temp import TempSensor
from .sensor import Sensor
from .asd import ASDSensor

ASSETS_PATH = pathlib.Path('../assets')


class SensorFactory:
    _instance: 'SensorFactory' = None

    @staticmethod
    def load_assets() -> None:
        GPSSensor.load_assets(ASSETS_PATH / 'gps_path.txt')
        ASDSensor.load_assets(ASSETS_PATH / 'asd.wav')

    def __init__(self, config: dict) -> None:
        SensorFactory.load_assets()
        self._configs_queue: SimpleQueue[dict] = SimpleQueue()
        self._last_id: int = 1
        sensor_config: dict
        for sensor_config in config:
            SensorFactory._validate_sensor_config(sensor_config)
            self._configs_queue.put(sensor_config)
        SensorFactory._instance = self

    @classmethod
    def _validate_sensor_config(cls, config: dict) -> None:
        cls._create(config, 1)

    @classmethod
    def get_instance(cls) -> 'SensorFactory':
        if cls._instance:
            return cls._instance
        else:
            raise ValueError("SensorFactory does not have any instance, create one before calling this method")

    @classmethod
    def _create(self, config: dict, id_num: int) -> Sensor:
        assert config.get('type') is not None, 'each sensor should have "type"'
        sensor_type: str = config['type']
        if sensor_type == 'device':
            return DeviceSensor(config, id_num)
        elif sensor_type == 'asd':
            return ASDSensor(config, id_num)
        elif sensor_type == 'camera':
            return CameraSensor(config, id_num)
        elif sensor_type == 'gps':
            return GPSSensor(config, id_num)
        elif sensor_type == 'temp':
            return TempSensor(config, id_num)
        else:
            raise NotImplemented(f'no such sensor type as {sensor_type}')

    def create(self) -> Sensor:
        config: dict = self._configs_queue.get()
        sensor: Sensor = SensorFactory._create(config, self._last_id)
        self._last_id += 1
        self._configs_queue.put(config)
        return sensor
