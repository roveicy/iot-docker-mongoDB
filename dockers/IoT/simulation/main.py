import asyncio
import time

import yaml
import logging
from simulation.sensor import SensorFactory, Sensor
from simulation.simulator import Simulator
from simulation.utils import is_number
import yarl
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

logger: logging.Logger = logging.getLogger()


def main() -> None:
    """
    driver code
    :return: None
    """
    host_url: yarl.URL = yarl.URL(os.environ.get("HOST_URL"))
    logger.info(f"web host url is: {host_url}")
    Sensor.HOST_URL = host_url

    with open('config/config.yaml', 'r') as config_file:
        total_config: dict = yaml.load(config_file, Loader=yaml.SafeLoader)
    logger.info('configuration loaded.')

    assert total_config.get('sensors'), 'config file should contain sensors configurations with "sensors" as key'
    sensor_factory: SensorFactory = SensorFactory(total_config.get('sensors'))

    event_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    assert total_config.get('schedule'), 'config file should contain schedule configurations with "schedule" as key'
    simulator: Simulator = Simulator(host_url, event_loop, total_config.get('schedule'))

    assert total_config.get('wait'), 'waiting times should be specified in configuration with "wait" as key'
    waiting_times = total_config.get('wait')
    assert is_number(waiting_times.get('start')), 'start waiting time should be a number'
    assert is_number(waiting_times.get('end')), 'end waiting time should be a number'

    time.sleep(waiting_times.get('start'))
    simulator.run()
    time.sleep(waiting_times.get('end'))


if __name__ == '__main__':
    main()
