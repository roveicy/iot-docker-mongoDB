import asyncio
import pathlib
import time

import yaml
import logging
from simulation.sensor import SensorFactory, Sensor
from simulation.simulator import Simulator
from simulation.utils import is_number
from simulation.consumers.file import FileMetricGenerator
from simulation.consumers.consumer import MetricGenerator
import yarl
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s'
)

logger: logging.Logger = logging.getLogger()


async def main() -> None:
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
    Sensor.simulator = simulator
    Sensor.result_queue = asyncio.Queue()

    assert total_config.get('wait'), 'waiting times should be specified in configuration with "wait" as key'
    waiting_times = total_config.get('wait')
    assert is_number(waiting_times.get('start')), 'start waiting time should be a number'
    assert is_number(waiting_times.get('end')), 'end waiting time should be a number'

    assert total_config.get('metrics'), 'metrics config should be specified in configuration with "metrics" as key'
    assert total_config.get('metrics').get('method'), \
        'metrics calculation method should be specified under "metrics[method]"'

    metric_generator: MetricGenerator
    if total_config['metrics']['method'] == 'file':
        assert total_config['metrics'].get('path'), 'you should specify filepath in metrics config'
        output_file_path: pathlib.Path = pathlib.Path(total_config['metrics']['path'])
        metric_generator = FileMetricGenerator(Sensor.result_queue, output_file_path)
    else:
        raise NotImplementedError(f'metric generation method {total_config["metric"]["method"]} not supported.')

    time.sleep(waiting_times.get('start'))
    logger.info("starting simulation")
    # producers
    simulation_task: asyncio.Task = event_loop.create_task(simulator.run())

    # consumers
    metric_generation: asyncio.Task = event_loop.create_task(metric_generator.consume())

    # wait for simulation to complete
    await asyncio.gather(simulation_task)

    # wait for results to be consumed
    await Sensor.result_queue.join()

    # cancel the consumer
    metric_generation.cancel()

    # wait for consumer to flush and cooldown
    await metric_generator.cooldown()

    time.sleep(waiting_times.get('end'))
    logger.info("simulation ended")


if __name__ == '__main__':
    asyncio.run(main())
