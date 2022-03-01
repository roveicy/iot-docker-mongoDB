import abc
import asyncio
import logging
from simulation.sensor.data import RequestResult

logger = logging.getLogger()


class ResultConsumer(abc.ABC):
    def __init__(self, queue: asyncio.Queue):
        self._queue: asyncio.Queue[RequestResult] = queue
        self._cancel: bool = False

    @abc.abstractmethod
    async def _cooldown(self):
        pass

    @abc.abstractmethod
    async def _warmup(self):
        pass

    def cancel(self):
        self._cancel = True

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
        await self._warmup()
        while not self._cancel:
            msg: RequestResult = await self._queue.get()
            if self._batch_done(msg):
                await self._flush()
            self._process_message(msg)
            self._queue.task_done()
        await self._flush()
        await self._cooldown()
