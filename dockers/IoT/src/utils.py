import time


def is_number(obj) -> bool:
    return type(obj) == int or type(obj) == float


def get_current_time() -> float:
    return round(time.time(), 5)
