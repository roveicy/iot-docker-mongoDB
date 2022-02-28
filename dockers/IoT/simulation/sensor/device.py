from .sensor import Sensor
from simulation.utils import is_number
from typing import Tuple
import random


class DeviceSensor(Sensor):
    _type: str = 'device'

    def __init__(self, config: dict, id_number: int):
        assert config.get('type') == 'device', f'sensor type should be device, got {config.get("type")}'
        super().__init__(config, id_number)

        assert is_number(config.get('mean')), 'device sensor config "mean" should be a number'
        self._mean: float = float(config['mean'])

        assert is_number(config.get('sigma')), 'device sensor config "sigma" should be a number'
        self._sigma: float = float(config['sigma'])

    def _get_data(self) -> Tuple[str, float]:
        value: str = random.choice(['ON', 'OFF'])
        scheduled_time: float = random.gauss(self._mean, self._sigma)
        return value, scheduled_time
