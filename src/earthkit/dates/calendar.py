import calendar
from enum import IntEnum


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


class MonthInYear:
    year: int
    month: int

    def __init__(self, year: int, month: int):
        self.year = year
        if month < 1 or month > 12:
            raise ValueError(f"Invalid month: {month}")
        self.month = month

    def length(self) -> int:
        res = _MONTH_LENGTHS[self.month]
        if isinstance(res, int):
            return res
        return res(self.year)

    def next(self) -> "MonthInYear":
        d, m = divmod(self.month, 12)
        m += 1
        return MonthInYear(self.year + d, m)

    def previous(self) -> "MonthInYear":
        d, m = divmod(self.month - 2, 12)
        m += 1
        return MonthInYear(self.year + d, m)
