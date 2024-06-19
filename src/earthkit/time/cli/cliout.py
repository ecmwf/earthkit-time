from datetime import date
from typing import Iterable


def format_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def format_date_list(dates: Iterable[date]) -> str:
    return "/".join(format_date(d) for d in dates)
