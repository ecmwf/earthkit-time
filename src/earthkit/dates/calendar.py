import calendar
from datetime import date
from enum import IntEnum
from typing import Union


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


def month_length(year: int, month: int):
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
