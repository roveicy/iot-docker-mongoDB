from queue import SimpleQueue
import typing
import pathlib

from .device import DeviceSensor
from .asd import ASDSensor
from .camera import CameraSensor
from .gps import GPSSensor
from .temp import TempSensor
from .sensor import Sensor

ASSETS_PATH = pathlib.Path('./assets')


class SensorFactory:
    _instance: 'SensorFactory' = None

    _sensor_inits: typing.Dict[str, typing.Callable[[dict, int], Sensor]] = {
        'device': DeviceSensor,
        'temp': TempSensor,
        'gps': GPSSensor,
        'camera': CameraSensor,
        'asd': ASDSensor
    }

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
            SensorFactory._validate_sensor_config(config)
            self._configs_queue.put(sensor_config)
        SensorFactory._instance = self

    @classmethod
    def _validate_sensor_config(cls, config: dict) -> None:
        assert config.get('type') is not None, 'each sensor should have "type"'
        sensor_type: str = config['type']
        sensor_init: typing.Callable[[dict, int], Sensor] = cls._sensor_inits.get(sensor_type)
        if sensor_init:
            sensor_init(config, 1)
        else:
            raise NotImplemented(f'no such sensor type as {sensor_type}')

    @classmethod
    def get_instance(cls) -> 'SensorFactory':
        if cls._instance:
            return cls._instance
        else:
            raise ValueError("SensorFactory does not have any instance, create one before calling this method")

    def create(self) -> Sensor:
        config: dict = self._configs_queue.get()
        sensor_type: str = config['type']
        sensor_init: typing.Callable[[dict, int], Sensor] = SensorFactory._sensor_inits.get(sensor_type)
        sensor: Sensor = sensor_init(config, self._last_id)
        self._last_id += 1
        self._configs_queue.put(config)
        return sensor
