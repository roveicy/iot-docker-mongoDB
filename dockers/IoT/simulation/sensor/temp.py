from .sensor import Sensor
import random
from simulation.utils import is_number
from typing import Tuple


class TempSensor(Sensor):
    _type: str = 'temp'

    def __init__(self, config: dict, id_number: int):
        assert config.get('type') == 'temp', f'sensor type should be temp, got {config.get("type")}'
        super().__init__(config, id_number)

        assert is_number(config.get('interval')) and config.get('interval') > 0, \
            'temp sensor config "interval" should be a positive number'
        self._interval: float = float(config.get('interval'))

        self._mean: float = random.uniform(-30, 30)

    def _get_data(self) -> Tuple[str, float]:
        value: str = f'{round(random.normalvariate(self._mean, 10), 1):.1f} C'
        return value, self._interval
