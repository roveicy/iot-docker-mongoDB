from typing import List, Any, Tuple
import logging
from pathlib import Path
import wave
import random

from .sensor import Sensor

logger = logging.getLogger()


class ASDSensor(Sensor):
    _type: str = 'asd'
    wave_data: List[Any] = []

    @classmethod
    def load_assets(cls, wave_file_path: Path) -> None:
        wave_file = wave.open(str(wave_file_path), 'rb')
        params = wave_file.getparams()
        logger.debug(f'wave file parameters:{params}')
        # params:  (2, 2, 48000, 2880000, 'NONE', 'not compressed')
        rate = float(params[2])
        # number of frames aggregated in each timestamp
        spl_per_ts = rate / 120
        asd_wrap_limit = int(params[3] / spl_per_ts)
        for i in range(0, asd_wrap_limit):
            data = wave_file.readframes(int(spl_per_ts))
            cls.wave_data.append(data)
        logger.info("Wave data: %d flames" % len(cls.wave_data))

    def __init__(self, config: dict, id_number: int):
        super().__init__(id_number)
        assert config.get('type') == 'asd', f'sensor type should be asd, got {config.get("type")}'

        assert type(config.get('sps')) == int and config.get('sps') > 0, \
            'asd sensor config "sps" should be a positive integer'
        self._sps: int = config.get('sps')

        self._spot: int = random.randrange(0, len(ASDSensor.wave_data), 1)

    def _get_data(self) -> Tuple[str, float]:
        current_spot: int = self._spot
        value = str(ASDSensor.wave_data[current_spot])
        self._spot = (current_spot + round(120 / self._sps)) % len(ASDSensor.wave_data)
        return value, (1 / self._sps)
