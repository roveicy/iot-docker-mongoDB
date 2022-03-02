import hashlib
import logging

from .db import DBManager
import sqlite3

logger = logging.getLogger()


class SQliteManager(DBManager):
    _schema_creation_query: str = """
    CREATE TABLE IF NOT EXISTS `sensor` (
     `id` bigint PRIMARY KEY,
     `device` varchar(32) NOT NULL,
     `ts` double NOT NULL,
     `seq` bigint NOT NULL,
     `dsize` int NOT NULL,
     `dhash` varchar(32) NOT NULL
    )
    """

    _sensor_list_query: str = """
        SELECT * FROM `sensor` LIMIT 10 OFFSET %d
        """

    _sensor_insertion_query: str = """
        INSERT INTO `sensor` (device, ts, seq, dsize, dhash) 
        VALUES (?,?,?,?,?)
        """

    def __init__(self):
        self._db = sqlite3.connect("iot.db")
        cursor = self._db.cursor()
        cursor.execute(SQliteManager._schema_creation_query)
        self._db.commit()
        cursor.close()

    def insert(self, record: dict):
        cursor = self._db.cursor()
        cursor.execute(SQliteManager._sensor_insertion_query,
                       (record["dev_id"], record["ts"], record["seq_no"], record["data_size"], record['hash']))
        self._db.commit()
        cursor.close()

    def query(self, page: int):
        assert page >= 0, 'page should be a positive integer'
        cursor = self._db.cursor()
        rows = cursor.execute(SQliteManager._sensor_list_query.format(page * 10))
        records = []
        for row in rows:
            records.append(
                {'id': row[0], 'device': row[1], 'ts': row[2], 'seq': row[3], 'size': row[4], 'hash': row[5]})
        cursor.close()
        return records
