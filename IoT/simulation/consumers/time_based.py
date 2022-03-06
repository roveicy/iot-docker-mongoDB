import abc
import asyncio
import datetime
import time
import typing
from abc import ABC

from .consumer import MetricGenerator
from ..sensor.data import RequestResult


class TimeBasedMetricsGenerator(MetricGenerator, ABC):
    """
    produces metrics every interval
    """

    def __init__(self, queue: asyncio.Queue[RequestResult], interval: datetime.timedelta):
        """
        :param queue: async message queue
        """
        super().__init__(queue)
        self._interval: datetime.timedelta = interval

        self._succeeded_requests: int = 0
        self._cumulative_response_time: float = 0
        self._total_requests: int = 0
        self._cumulative_sensor_count: int = 0
        self._first_sending_timestamp: typing.Optional[datetime.datetime] = None
        self._last_sending_timestamp: typing.Optional[datetime.datetime] = None
        self._last_flush: datetime.datetime = datetime.datetime.now()

    def _batch_done(self, msg: RequestResult) -> bool:
        return datetime.datetime.now() - self._last_flush >= self._interval

    def _process_message(self, msg: RequestResult):
        self._total_requests += 1
        self._succeeded_requests += msg.is_okay
        self._cumulative_response_time += msg.response_time.total_seconds() if msg.response_time else 0
        self._cumulative_sensor_count += msg.current_sensor_count
        if not self._first_sending_timestamp or msg.send_time < self._first_sending_timestamp:
            self._first_sending_timestamp = msg.send_time
        if not self._last_sending_timestamp or msg.send_time > self._last_sending_timestamp:
            self._last_sending_timestamp = msg.send_time

    async def _flush(self):
        self._last_flush = datetime.datetime.now()
        err_rate: float = 1 - self._succeeded_requests / self._total_requests
        avg_response_time: float = (self._cumulative_response_time / self._succeeded_requests) \
            if self._succeeded_requests else None
        # response time is only available for succeeded requests
        avg_sensors: float = self._cumulative_sensor_count / self._total_requests
        await self._send_metrics(self._first_sending_timestamp, self._last_sending_timestamp, avg_sensors,
                                 self._total_requests, err_rate,
                                 avg_response_time)
        self._total_requests = 0
        self._succeeded_requests = 0
        self._cumulative_response_time = 0
        self._cumulative_sensor_count = 0
        self._first_sending_timestamp = None
        self._last_sending_timestamp = None

    @abc.abstractmethod
    async def _send_metrics(self, first_sending_time: datetime.datetime, last_sending_time: datetime.datetime,
                            avg_sensors: float, total_requests: int,
                            err_rate: float,
                            avg_response_time: float):
        pass
