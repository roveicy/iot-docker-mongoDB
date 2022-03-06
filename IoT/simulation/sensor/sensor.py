import abc
import asyncio
import dataclasses
import datetime
import logging
import time
from .data import SensorMessage, RequestResult
from typing import Tuple

import aiohttp
import yarl

from simulation.utils import get_current_time

logger = logging.getLogger()


class Sensor(abc.ABC):
    HOST_URL: yarl.URL = None
    result_queue: asyncio.Queue[RequestResult]
    simulator: 'Simulator'

    def __init__(self, id_number: int):
        self._sequence_number: int = 0
        self._id: int = id_number
        self._session: aiohttp.ClientSession = aiohttp.ClientSession()
        self._cancel: bool = False

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

    def cancel(self):
        self._cancel = True

    @property
    def id(self) -> str:
        return f'{self._type}_{self._id}'

    async def _send_message(self, msg: SensorMessage) -> RequestResult:
        start: datetime.datetime = datetime.datetime.now()
        try:
            async with self._session.post(Sensor.HOST_URL, json=dataclasses.asdict(msg)) as response:
                end: datetime.datetime = datetime.datetime.now()
                response_time: datetime.timedelta = end - start
                status_code: int = response.status
                is_okay: bool = (200 <= status_code < 300)
                if not is_okay:
                    logger.debug(f"INVALID RESPONSE: [status: {status_code},content: {response.content}]")
                return RequestResult(is_okay, start, Sensor.simulator.current_sensors, status_code, response_time)

        except aiohttp.ClientError as e:
            logger.debug(f"CLIENT ERROR: {e}")
            return RequestResult(False, start, Sensor.simulator.current_sensors)

    async def run(self) -> None:
        logger.info(f"Sensor {self.id}: start.")
        while not self._cancel:
            start: float = time.time()
            msg: SensorMessage
            st: float
            msg, st = self._get_message()
            result: RequestResult = await self._send_message(msg)
            await Sensor.result_queue.put(result)
            diff: float = st - (time.time() - start)
            if diff > 0:
                await asyncio.sleep(diff)

        await self._session.close()
        logger.info(f"Sensor {self.id}: stop.")
