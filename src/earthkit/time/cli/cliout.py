from datetime import date, datetime
from typing import Iterable


def format_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def format_date_list(dates: Iterable[date], sep: str = "/") -> str:
    return sep.join(format_date(d) for d in dates)


def format_datetime(d: datetime) -> str:
    return d.strftime("%Y%m%d%H")
