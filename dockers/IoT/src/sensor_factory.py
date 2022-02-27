from queue import SimpleQueue
import typing

from dockers.IoT.src.sensors import ASDSensor, CameraSensor, DeviceSensor, GPSSensor, Sensor, TempSensor

class SensorFactory:
    _last_id: int = 1
    _sensor_inits: typing.Dict[str,function] = {
        'device': DeviceSensor,
        'temp': TempSensor,
        'gps': GPSSensor,
        'camera': CameraSensor,
        'asd': ASDSensor
    }

    def __init__(self, config:dict) -> None:
        self._configs_queue: SimpleQueue[dict] = SimpleQueue()
        sensor_config: dict
        for sensor_config in config:
            SensorFactory._validate_sesnor_config(config)
            self._configs_queue.put(sensor_config)

    @staticmethod
    def _validate_sensor_config(config: dict) -> None:
        assert config.get('type') is not None, 'each sensor should have "type"'
        sensor_type: str = config['type']
        sensor_init: function = SensorFactory._sensor_inits.get(sensor_type)
        if sensor_init:
            sensor_init(config,1)
        else:
            raise NotImplemented(f'no such sensor type as {sensor_type}')

    def create(self) -> Sensor:
        config: dict = self._configs_queue.get()
        sensor_type: str = config['type']
        sensor_init: function = SensorFactory._sensor_inits.get(sensor_type)
        sensor: Sensor = sensor_init(config,self._last_id)
        self._last_id += 1
        return sensor
