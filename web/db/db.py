import abc


class DBManager(abc.ABC):

    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def insert(self, record: dict):
        pass

    @abc.abstractmethod
    def query(self, page: int):
        pass
