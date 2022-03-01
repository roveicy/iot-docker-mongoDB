import asyncio
import logging
import queue
import time
from dataclasses import dataclass
from typing import Tuple
from queue import SimpleQueue
import yarl
from sensor import SensorFactory, Sensor

logger = logging.getLogger()


@dataclass
class SchedulePiece:
    sensors_count: int
    time: int


class Simulator:

    def __init__(self, url: yarl.URL, event_loop: asyncio.AbstractEventLoop, schedule_config: dict):
        """
        :param url: backend host url
        :param event_loop: event loop to put tasks in
        """
        self._url: yarl.URL = url
        self._loop: asyncio.AbstractEventLoop = event_loop
        self._tasks: queue.LifoQueue[Tuple[Sensor, asyncio.Task]] = queue.LifoQueue()
        self._running: bool = False  # todo: remove this if not necessary
        self._schedule: SimpleQueue[SchedulePiece] = SimpleQueue()
        self._sensor_factory: SensorFactory = SensorFactory.get_instance()

        assert len(schedule_config) > 0, 'schedule configuration should contain something'

        for config in schedule_config:
            assert type(config.get('sensors')) == int, \
                f'number of sensors in each schedule piece configuration must be an integer' \
                f', got {config.get("sensors")}'
            assert type(config.get('time')) == int, \
                f'time of each schedule piece configuration must be an integer, got {config.get("time")}'

            self._schedule.put(SchedulePiece(config['sensors'], config['time']))
        Simulator._instance = self

    @property
    def current_sensors(self) -> int:
        return self._tasks.qsize()

    def _deploy_sensors(self, count: int):
        for i in range(count):
            sensor: Sensor = self._sensor_factory.create()
            running_task: asyncio.Task = self._loop.create_task(sensor.run())
            self._tasks.put((sensor, running_task))
        logger.info(f'{count} sensors deployed.')

    def _remove_sensors(self, count: int):
        assert count <= self._tasks.qsize(), f'trying to remove {count} sensors, only {self._tasks.qsize()} available.'
        for i in range(count):
            sensor: Sensor
            running_task: asyncio.Task
            sensor, running_task = self._tasks.get()
            sensor.cancel()
            # we can save sensors for later use too
        logger.info(f'{count} sensors removed.')

    async def run(self):
        logger.info("Simulator started.")
        self._running = True
        i: int = 1
        while not self._schedule.empty():
            start_time = time.time()

            piece: SchedulePiece = self._schedule.get()
            logger.info(f"Schedule {i}: [sensors:{piece.sensors_count}, time:{piece.time}]")

            if self.current_sensors < piece.sensors_count:
                self._deploy_sensors(piece.sensors_count - self.current_sensors)
            elif self.current_sensors > piece.sensors_count:
                self._remove_sensors(self.current_sensors - piece.sensors_count)

            logger.info(f"Schedule {i}: [current_sensors:{self.current_sensors}]")

            wait_time: float = piece.time - (time.time() - start_time)
            await asyncio.sleep(wait_time)
        self._remove_sensors(self.current_sensors)
        self._running = False
        logger.info("Simulator stopped.")
