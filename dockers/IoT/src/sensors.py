import abc
import yarl


# class Simulator:
# def __init__(self,url:yarl.URL):

class Sensor(abc.ABC):

    def __init__(self, config: dict):
        pass

    @abc.abstractmethod
    def get_message(self):
        pass



class DeviceSensor(Sensor):
    def __init__(self, config: dict):
        super().__init__(config)
        assert type(config.get('mean')) is not None, 'device sensor needs "mean" config'
        self._mean: float = float(config['mean'])
        assert config.get('mean') is not None, 'device sensor needs "mean" config'
        self._sigma: float = float(config['sigma'])

    def parse_config(self, config: dict):
        assert config.get('type') == 'device', f'sensor type should be device, got {config.get("type")}'
