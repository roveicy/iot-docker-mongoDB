import abc
import asyncio


class MetricConsumer(abc.ABC):
    def __init__(self, queue: asyncio.Queue):
        self._queue: asyncio.Queue = queue

    async def run(self):
        pass
