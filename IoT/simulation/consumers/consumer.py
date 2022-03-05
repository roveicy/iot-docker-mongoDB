import abc
import asyncio
import logging
from simulation.sensor.data import RequestResult

logger = logging.getLogger()


class MetricGenerator(abc.ABC):
    def __init__(self, queue: asyncio.Queue):
        self._queue: asyncio.Queue[RequestResult] = queue

    @abc.abstractmethod
    async def _cooldown(self):
        pass

    @abc.abstractmethod
    def _warmup(self):
        pass

    @abc.abstractmethod
    def _process_message(self, msg: RequestResult):
        pass

    @abc.abstractmethod
    def _batch_done(self, msg: RequestResult) -> bool:
        pass

    @abc.abstractmethod
    async def _flush(self):
        pass

    async def consume(self):
        self._warmup()
        while True:
            msg: RequestResult = await self._queue.get()
            if self._batch_done(msg):
                await self._flush()
            self._process_message(msg)
            self._queue.task_done()

    async def cooldown(self):
        await self._flush()
        await self._cooldown()
