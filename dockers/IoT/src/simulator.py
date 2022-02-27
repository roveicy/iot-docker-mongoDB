import asyncio
import typing

import yarl


class Simulator:
    def __init__(self, url: yarl.URL, event_loop: asyncio.AbstractEventLoop, schedule: dict):
        """
        :param url: backend host url
        :param event_loop: event loop to put tasks in
        """
        self._url: yarl.URL = url
        self._loop: asyncio.AbstractEventLoop = event_loop
        self._current_sensors: int = 0
        self.tasks: typing.List = []  # todo: investigate this
        # todo: implement metrics handler (prometheus/file/message queue)
        self._running = False
        # todo: pass schedule and sensor configs

    async def run(self):
        pass
