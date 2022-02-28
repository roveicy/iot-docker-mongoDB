from typing import List, Tuple
from pathlib import Path
import csv
import logging
import random

from .sensor import Sensor
from simulation.utils import is_number

logger = logging.getLogger()


class GPSSensor(Sensor):
    paths: List[Tuple[float, float, float]] = []
    _type: str = 'gps'

    @classmethod
    def load_assets(cls, gps_file_path: Path) -> None:
        with open(gps_file_path, 'r') as gpsfile:
            p = csv.reader(gpsfile, delimiter='\t')
            for idx, row in enumerate(p):
                assert len(row) >= 3, f'path file rows should include at least 3 cells, row {idx + 1} is:\n{row}'
                cls.paths.append((float(row[0]), float(row[1]), float(row[2])))
        logger.info(f'GPS paths loaded: {len(cls.paths)} rows')

    def __init__(self, config: dict, id_number: int):
        super().__init__(id_number)
        assert config.get('type') == 'gps', f'sensor type should be gps, got {config.get("type")}'

        assert is_number(config.get('interval')) and config.get('interval') > 0, \
            'gps sensor config "interval" should be a positive number'
        self._interval: float = float(config.get('interval'))

        self._dir: bool = True
        self._spot: int = random.randrange(0, len(GPSSensor.paths), 1)

    def _get_data(self) -> Tuple[str, float]:
        current_spot: int = self._spot
        value: str = f'({GPSSensor.paths[current_spot][0]},{GPSSensor.paths[current_spot][1]})'
        if self._dir:
            current_spot += 1
            if current_spot >= len(GPSSensor.paths):
                current_spot = len(GPSSensor.paths) - 2
                self._dir = False
        else:
            current_spot -= 1
            if current_spot < 0:
                current_spot = 1
                self._dir = True

        self._spot = current_spot
        return value, self._interval
