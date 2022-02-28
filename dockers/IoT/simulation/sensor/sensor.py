import abc
import dataclasses
import logging
from typing import Tuple

import aiohttp
import yarl

from simulation.utils import is_number, get_current_time

logger = logging.getLogger()


@dataclasses.dataclass
class SensorMessage:
    dev_id: str  # device id
    ts: float  # timestamp
    seq_no: int  # sequence number
    data_size: int
    sensor_data: str


class Sensor(abc.ABC):
    HOST_URL: yarl.URL = None

    def __init__(self, config: dict, id_number: int):
        self._sequence_number: int = 0
        self._id: int = id_number
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()

    @classmethod
    @property
    @abc.abstractmethod
    def _type(self) -> str:
        """
        :return: sensor_type
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_data(self) -> Tuple[str, float]:
        """
        :return: data: str -> sensor data , scheduled_time: float
        scheduled time will be used in scheduling sleep time for this sensor
        """
        raise NotImplementedError

    def _get_message(self) -> Tuple[SensorMessage, float]:
        """
        :return: message: str -> json serialized sensor message , scheduled_time: float
        """
        data: str
        scheduled_time: float  # move scheduled_time if not necessary
        data, scheduled_time = self._get_data()
        message: SensorMessage = SensorMessage(
            self.id,
            get_current_time(),
            self._sequence_number,
            len(data),
            data
        )
        self._sequence_number += 1
        return message, scheduled_time

    @property
    def id(self) -> str:
        return f'{self._type}_{self._id}'

    async def _send_message(self, msg: SensorMessage) -> None:
        try:
            async with self._session.post(Sensor.HOST_URL, json=dataclasses.asdict(msg)) as response:
                pass
        # todo: calculate metrics and send to queue
        except aiohttp.ClientError:
            pass

    async def run(self) -> None:
        # todo: implement
        pass
