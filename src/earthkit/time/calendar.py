import calendar
from datetime import date, datetime
from enum import IntEnum
from typing import Tuple, Union


class Weekday(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


MONDAY = Weekday.MONDAY
TUESDAY = Weekday.TUESDAY
WEDNESDAY = Weekday.WEDNESDAY
THURSDAY = Weekday.THURSDAY
FRIDAY = Weekday.FRIDAY
SATURDAY = Weekday.SATURDAY
SUNDAY = Weekday.SUNDAY


def to_weekday(arg: Union[int, str]) -> Weekday:
    """Convert integers and strings to weekdays

    Any unambiguous prefix of a weekday name will be accepted, and case is
    ignored.
    """
    if isinstance(arg, str) and arg.isdigit():
        arg = int(arg)
    if isinstance(arg, int):
        if arg not in range(7):
            raise ValueError(f"Week day out of range: {arg} not in 0-6")
        return Weekday(arg)
    arg = arg.upper()
    matching = [wd for wd in Weekday if wd.name.startswith(arg)]
    if not matching:
        raise ValueError(f"Unrecognised week day: {arg!r}")
    if len(matching) > 1:
        others = ", ".join(wd.name.capitalize() for wd in matching)
        raise ValueError(f"Ambiguous week day: {arg!r} could be any of {others}")
    return matching[0]


_MONTH_LENGTHS = [
    None,
    31,
    (lambda year: 29 if calendar.isleap(year) else 28),
    31,
    30,
    31,
    30,
    31,
    31,
    30,
    31,
    30,
    31,
]


def month_length(year: int, month: int) -> int:
    """Return the number of days of a given month"""
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month}")
    mlen = _MONTH_LENGTHS[month]
    if isinstance(mlen, int):
        return mlen
    return mlen(year)


def day_exists(year: int, month: int, day: int) -> bool:
    """Check whether a given day exists in the calendar"""
    if month < 1 or month > 12:
        return False
    if day < 1 or day > month_length(year, month):
        return False
    return True


class MonthInYear:
    year: int
    month: int

    def __init__(self, year: int, month: int):
        self.year = year
        if month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}")
        self.month = month

    def __contains__(self, day: Union[int, date]) -> bool:
        if isinstance(day, date):
            if day.year != self.year:
                return False
            if day.month != self.month:
                return False
            day = day.day
        if day < 1 or day > self.length():
            return False
        return True

    def length(self) -> int:
        return month_length(self.year, self.month)

    def next(self) -> "MonthInYear":
        d, m = divmod(self.month, 12)
        m += 1
        return MonthInYear(self.year + d, m)

    def previous(self) -> "MonthInYear":
        d, m = divmod(self.month - 2, 12)
        m += 1
        return MonthInYear(self.year + d, m)


def parse_mmdd(arg: Union[Tuple[int, int], str]) -> Tuple[int, int]:
    """Convert pairs of ints or MMDD strings into (month, day) pairs"""
    if not isinstance(arg, str):
        m, d = arg
        if not day_exists(2000, m, d):
            raise ValueError(f"Invalid day: {d} not in 1-{month_length(2000, m)}")
        return (m, d)
    if len(arg) != 4:
        raise ValueError(f"Unrecognised month-day value: {arg!r}")
    mm = arg[:2]
    dd = arg[2:]
    if not mm.isdigit() or not dd.isdigit():
        raise ValueError(f"Unrecognised month-day value: {arg!r}")
    m = int(mm)
    if m not in range(1, 13):
        raise ValueError(f"Invalid month: {m} not in 1-12")
    d = int(dd)
    if not day_exists(2000, m, d):
        raise ValueError(f"Invalid day: {d} not in 1-{month_length(2000, m)}")
    return (m, d)


def parse_date(arg: Union[str, Tuple[int, int, int]]) -> date:
    if not isinstance(arg, str):
        y, m, d = arg
        if not day_exists(y, m, d):
            raise ValueError(f"Invalid date: {arg!r}")
        return date(y, m, d)
    try_formats = ["%Y%m%d"]
    dt = None
    for fmt in try_formats:
        try:
            dt = datetime.strptime(arg, fmt)
        except ValueError:
            continue
        else:
            break
    if dt is None:
        raise ValueError(f"Unrecognised date format: {arg!r}")
    return dt.date()
