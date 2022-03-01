import datetime
import logging
import pathlib
import typing

import aiofiles

from .time_based import TimeBasedMetricsGenerator
from ..sensor.data import RequestResult
import asyncio

logger = logging.getLogger()


class FileMetricGenerator(TimeBasedMetricsGenerator):

    def __init__(self, queue: asyncio.Queue[RequestResult], output_path: pathlib.Path):
        """
        :param queue: async message queue
        :param output_path: filepath to write metrics in (as a path object)
        """
        super(FileMetricGenerator, self).__init__(queue)

        self._output_path: pathlib.Path = output_path
        self._output_file: typing.IO[typing.AnyStr]

    async def _warmup(self):
        logger.info(f"writing metrics to {self._output_path.absolute()}:")
        self._output_file = await aiofiles.open(self._output_path, 'w')
        await self._output_file.write("time_till,average_sensors,requests,err_rate,average_response_time\n")

    async def _cooldown(self):
        await self._output_file.close()
        logger.info(f"metrics wrote to {self._output_path.absolute()}")

    async def _send_metrics(self, time: datetime.datetime, avg_sensors: float, total_requests: int, err_rate: float,
                            avg_response_time: float):
        await self._output_file.write(
            f'{time.strftime("%H:%M:%S")},{avg_sensors:.2f},{self._total_requests},{err_rate:.2f},{avg_response_time:.2f}\n')
