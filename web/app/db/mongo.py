import hashlib
import logging
import os
import typing

import pymongo
from pymongo.errors import PyMongoError, ConnectionFailure
from pymongo import MongoClient

from .db import DBManager

logger = logging.getLogger()


class MongoManager(DBManager):
    def __init__(self):
        user: str = os.environ.get("WEB_WORKLOAD_CONFIG_MONGODB_USERNAME")
        password: str = os.environ.get("WEB_WORKLOAD_CONFIG_MONGODB_PASSWORD")
        self._client: pymongo.MongoClient = MongoClient(f"mongodb://{user}:{password}@db:27017/",
                                                        serverSelectionTimeoutMS=500)
        try:
            # The ismaster command is cheap and does not require auth.
            self._client.admin.command('ismaster')
        except ConnectionFailure as e:
            logger.error("server not available")
            raise e
        self._db = self._client.iot
        self._collection = self._db.sensors

    def insert(self, record: dict) -> bool:
        """
        :param record: request data record
        :return: if operation was successful
        """
        try:
            self._collection.insert_one({
                "device": record["dev_id"],
                "ts": record["ts"],
                "seq": record["seq_no"],
                "data": record["sensor_data"][0:32],
                "size": record["data_size"],
                "hash": record['hash']
            })
            return True
        except PyMongoError as e:
            logger.error(e)
            return False

    def query(self, page: int) -> typing.Union[typing.List[dict], None]:
        records = []
        try:
            for r in self._collection.find().limit(10).skip(page * 10):
                records.append(r)
            return records
        except PyMongoError as e:
            logger.error(e)
            return None
