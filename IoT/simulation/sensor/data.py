import dataclasses
import datetime
import typing


@dataclasses.dataclass
class SensorMessage:
    dev_id: str  # device id
    ts: float  # timestamp
    seq_no: int  # sequence number
    data_size: int
    sensor_data: str


@dataclasses.dataclass
class RequestResult:
    is_okay: bool
    send_time: datetime.datetime
    current_sensor_count: int
    status_code: typing.Optional[int] = None
    response_time: typing.Optional[datetime.timedelta] = None
