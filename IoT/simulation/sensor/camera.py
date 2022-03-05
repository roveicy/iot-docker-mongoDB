import random
import os
from typing import Tuple
from base64 import b64encode

from .sensor import Sensor


class CameraSensor(Sensor):
    _type: str = 'camera'

    def __init__(self, config: dict,
                 id_number: int):
        super().__init__(id_number)
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
