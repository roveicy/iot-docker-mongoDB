import abc
import asyncio
import datetime
from abc import ABC

from .consumer import MetricGenerator
from ..sensor.data import RequestResult


class TimeBasedMetricsGenerator(MetricGenerator, ABC):
    """
    produces metrics every one minute
    # todo: generalize 'one minute' to every timedelta
    """

    def __init__(self, queue: asyncio.Queue[RequestResult]):
        """
        :param queue: async message queue
        """
        super().__init__(queue)

        self._succeeded_requests: int = 0
        self._cumulative_response_time: float = 0
        self._total_requests: int = 0
        self._cumulative_sensor_count: int = 0
        self._last_sending_timestamp: datetime.datetime = datetime.datetime.now()

    def _batch_done(self, msg: RequestResult) -> bool:
        return msg.send_time.minute != self._last_sending_timestamp.minute \
               and msg.send_time > self._last_sending_timestamp

    def _process_message(self, msg: RequestResult):
        self._total_requests += 1
        self._succeeded_requests += msg.is_okay
        self._cumulative_response_time += msg.response_time
        self._cumulative_sensor_count += msg.current_sensor_count
        self._last_sending_timestamp = msg.send_time

    async def _flush(self):
        time: datetime.datetime = self._last_sending_timestamp
        err_rate: float = 1 - self._succeeded_requests / self._total_requests
        avg_response_time: float = self._cumulative_response_time / self._total_requests
        avg_sensors: float = self._cumulative_sensor_count / self._total_requests
        await self._send_metrics(time, avg_sensors, self._total_requests, err_rate, avg_response_time)
        self._total_requests = 0
        self._succeeded_requests = 0
        self._cumulative_response_time = 0
        self._cumulative_sensor_count = 0

    @abc.abstractmethod
    async def _send_metrics(self, time: datetime.datetime, avg_sensors: float, total_requests: int, err_rate: float,
                            avg_response_time: float):
        pass
