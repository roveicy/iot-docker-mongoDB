import abc
import json
import os
import random
import csv
import logging
import wave
from typing import List, Tuple, Any
from pathlib import Path
from base64 import b64encode

import aiohttp

from .utils import is_number, get_current_time

logger = logging.getLogger()


# class Simulator:
# def __init__(self,url:yarl.URL):

class Sensor(abc.ABC):
    def __init__(self, config: dict, id_number: int):
        self._sequence_number: int = 0
        self._id: int = id_number
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()

    @abc.abstractmethod
    def _get_data(self) -> Tuple[str, float]:
        """
        :return: data: str -> sensor data , scheduled_time: float
        scheduled time will be used in scheduling sleep time for this sensor
        """
        raise NotImplementedError

    def _get_message(self) -> Tuple[str, float]:
        """
        :return: message: str -> json serialized sensor message , scheduled_time: float
        """
        data: str
        scheduled_time: float  # move scheduled_time if not necessary
        data, scheduled_time = self._get_data()
        message = {
            'dev_id': self.id,  # device_id
            'ts': get_current_time(),  # timestamp
            'seq_no': self._sequence_number,
            'data_size': len(data),
            'sensor_data': data
        }
        self._sequence_number += 1
        return json.dumps(message), scheduled_time

    @property
    def id(self) -> str:
        return f'{self._type}_{self._id}'

    @classmethod
    @property
    @abc.abstractmethod
    def _type(self) -> str:
        """
        :return: sensor_type
        """
        raise NotImplementedError


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
        super().__init__(config, id_number)
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


class CameraSensor(Sensor):
    _type: str = 'camera'

    def __int__(self, config: dict, id_number: int):
        super().__init__(config, id_number)
        assert config.get('type') == 'camera', f'sensor type should be camera, got {config.get("type")}'

        assert type(config.get('fps')) == int and config.get('fps') > 0, \
            'camera sensor config "fps" should be a positive integer'
        self._fps: int = config.get('fps')

        assert type(config.get('bitrate')) == int and config.get('bitrate') > 0, \
            'camera sensor config "bitrate" should be a positive integer'
        self._bitrate: int = config.get('bitrate')

        self._motion: bool = random.choice((True, False))
        self._motion_time: float = random.uniform(1, 10)
        self._current_time: int = 0

    def _get_data(self) -> Tuple[str, float]:
        new_motion: bool = False
        if self._motion:
            bitrate = int(random.uniform(self._bitrate / 4, self._bitrate))
            value: str = b64encode(os.urandom((int(bitrate / 8 / self._fps)))).decode('utf-8')
            scheduled_time: float = 1.0 / self._fps
            self._current_time += scheduled_time
            if self._current_time > self._motion_time:
                new_motion = True
        else:
            value: str = 'NO_MOTION'
            scheduled_time: float = self._motion_time
            new_motion = True

        if new_motion:
            self._motion = random.choice((True, False))
            self._motion_time = random.uniform(1, 10)
            self._current_time = 0
        return value, scheduled_time


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

    def __int__(self, config: dict, id_number: int):
        super().__init__(config, id_number)
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
