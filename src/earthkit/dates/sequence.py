from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Container, Iterable, Iterator, Tuple, Union

from .calendar import MonthInYear, Weekday, day_exists


class Sequence(ABC):
    """Abstract representation of a sequence of dates

    Minimal implementation requirement: ``__contains__``. Implementing ``next``
    and ``previous`` is highly recommended for efficiency.
    """

    @abstractmethod
    def __contains__(self, reference: date) -> bool:
        raise NotImplementedError

    def next(self, reference: date, strict: bool = True) -> date:
        """Return the next date in the sequence, after ``reference``.
        If ``strict`` is ``False`` and ``reference`` is in the sequence, it is
        returned.
        """
        if not strict and reference in self:
            return reference
        oneday = timedelta(days=1)
        current = reference + oneday
        while current not in self:
            current += oneday
        return current

    def previous(self, reference: date, strict: bool = True) -> date:
        """Return the previous date in the sequence, before ``reference``.
        If ``strict`` is ``False`` and ``reference`` is in the sequence, it is
        returned.
        """
        if not strict and reference in self:
            return reference
        oneday = timedelta(days=1)
        current = reference - oneday
        while current not in self:
            current -= oneday
        return current

    def range(
        self,
        start: date,
        end: date,
        include_start: bool = True,
        include_end: bool = True,
    ) -> Iterator[date]:
        """Return all matching dates between ``start`` and ``end``.
        ``include_start`` and ``include_end`` control whether ``start`` and
        ``end`` are returned if they are in the sequence.
        """
        if end < start:
            raise ValueError("Start date should be before end date")

        current = self.next(start, strict=(not include_start))
        last = self.previous(end, strict=(not include_end))
        while current <= last:
            yield current
            current = self.next(current)

    def bracket(
        self, reference: date, num: Union[int, Tuple[int, int]] = 1, strict: bool = True
    ) -> Iterator[date]:
        """Return matching dates around ``reference``

        Parameters
        ----------
        reference: date
            Reference date
        num: int or (int, int) tuple
            Number of dates to include either side of ``reference``. If a single
            value is given, it is used on both sides
        strict: bool
            If ``False`` and ``reference`` is in the sequence, it will be
            returned as well (not counted in ``num``)
        """
        if isinstance(num, int):
            before = after = num
        else:
            before, after = num

        if before <= 0 or after <= 0:
            raise ValueError("`num` values must be positive")

        start = reference
        for _ in range(before):
            start = self.previous(start)

        end = reference
        for _ in range(after):
            end = self.next(end)

        for current in self.range(start, end):
            if strict and current == reference:
                continue
            yield current


class DailySequence(Sequence):
    """Sequence of consecutive dates

    Any day number (in the month) present in ``excludes`` will be skipped
    """

    def __init__(self, excludes: Container[int] = {}):
        self.excludes = excludes

    def __contains__(self, reference: date) -> bool:
        return reference.day not in self.excludes

    def __repr__(self) -> str:
        return f"DailySequence(excludes={self.excludes!r})"


class WeeklySequence(Sequence):
    """Sequence of dates happening on given days of each week"""

    def __init__(self, days: Union[int, Weekday, Iterable[int], Iterable[Weekday]]):
        if isinstance(days, (int, Weekday)):
            self.days = [Weekday(days)]
        else:
            self.days = sorted(Weekday(day) for day in days)
        if not self.days:
            raise ValueError("`days` cannot be empty")

    def __contains__(self, reference: date) -> bool:
        wday = Weekday(reference.weekday())
        return wday in self.days

    def __repr__(self) -> str:
        repr_days = ", ".join([day.name for day in self.days])
        return f"WeeklySequence(days=[{repr_days}])"

    def next(self, reference: date, strict: bool = True) -> date:
        wday = Weekday(reference.weekday())
        if wday in self.days and not strict:
            return reference
        new_wday = next((day for day in self.days if day > wday), self.days[0])
        delta = new_wday - wday
        assert -7 < delta < 7
        if delta > 0:
            return reference + timedelta(days=delta)
        else:
            return reference + timedelta(days=(delta + 7))

    def previous(self, reference: date, strict: bool = True) -> date:
        wday = Weekday(reference.weekday())
        if wday in self.days and not strict:
            return reference
        new_wday = next((day for day in self.days[::-1] if day < wday), self.days[-1])
        delta = new_wday - wday
        assert -7 < delta < 7
        if delta < 0:
            return reference + timedelta(days=delta)
        else:
            return reference + timedelta(days=(delta - 7))


class MonthlySequence(Sequence):
    """Sequence of dates happening on given days of each month

    Any ``(month, day)`` tuple present in ``excludes`` will be skipped
    """

    def __init__(
        self, days: Union[int, Iterable[int]], excludes: Container[Tuple[int, int]] = {}
    ):
        if isinstance(days, int):
            self.days = [days]
        else:
            self.days = sorted(days)
        if not self.days:
            raise ValueError("`days` cannot be empty")
        if any((day < 1 or day > 31) for day in self.days):
            raise ValueError("All days must be between 1 and 31")
        self.excludes = excludes

    def __contains__(self, reference: date) -> bool:
        return (
            reference.day in self.days
            and (reference.month, reference.day) not in self.excludes
        )

    def __repr__(self) -> str:
        return f"MonthlySequence(days={self.days!r}, excludes={self.excludes!r})"

    def next(self, reference: date, strict: bool = True) -> date:
        if not strict and reference in self:
            return reference
        ymonth = MonthInYear(reference.year, reference.month)
        new_day = next(
            (
                day
                for day in self.days
                if day > reference.day
                and day in ymonth
                and (ymonth.month, day) not in self.excludes
            ),
            None,
        )
        while new_day is None:
            ymonth = ymonth.next()
            for day in self.days:
                if day in ymonth and (ymonth.month, day) not in self.excludes:
                    new_day = day
                    break
        return date(ymonth.year, ymonth.month, new_day)

    def previous(self, reference: date, strict: bool = True) -> date:
        if not strict and reference in self:
            return reference
        ymonth = MonthInYear(reference.year, reference.month)
        new_day = next(
            (
                day
                for day in self.days[::-1]
                if day < reference.day
                and day in ymonth
                and (ymonth.month, day) not in self.excludes
            ),
            None,
        )
        while new_day is None:
            ymonth = ymonth.previous()
            for day in self.days[::-1]:
                if day in ymonth and (ymonth.month, day) not in self.excludes:
                    new_day = day
                    break
        return date(ymonth.year, ymonth.month, new_day)


class YearlySequence(Sequence):
    """Sequence of dates happening on given days of each year (in (month, day) format)"""

    def __init__(
        self,
        days: Union[Tuple[int, int], Iterable[Tuple[int, int]]],
        excludes: Container[date] = {},
    ):
        if (
            isinstance(days, tuple)
            and len(days) == 2
            and all(isinstance(day, int) for day in days)
        ):
            self.days = [days]
        else:
            self.days = sorted(days)
        self.excludes = excludes

    def __contains__(self, reference: date) -> bool:
        return (
            reference.month,
            reference.day,
        ) in self.days and reference not in self.excludes

    def __repr__(self) -> str:
        return f"YearlySequence(days={self.days!r}, excludes={self.excludes!r})"

    def next(self, reference: date, strict: bool = True) -> date:
        if not strict and reference in self:
            return reference

        year = reference.year
        new_month, new_day = next(
            (
                (month, day)
                for month, day in self.days
                if day_exists(year, month, day)
                and (month, day) > (reference.month, reference.day)
                and date(year, month, day) not in self.excludes
            ),
            (None, None),
        )
        while new_day is None:
            year += 1
            for month, day in self.days:
                if (
                    day_exists(year, month, day)
                    and date(year, month, day) not in self.excludes
                ):
                    new_month = month
                    new_day = day
                    break
        return date(year, new_month, new_day)

    def previous(self, reference: date, strict: bool = True) -> date:
        if not strict and reference in self:
            return reference

        year = reference.year
        new_month, new_day = next(
            (
                (month, day)
                for month, day in self.days[::-1]
                if day_exists(year, month, day)
                and (month, day) < (reference.month, reference.day)
                and date(year, month, day) not in self.excludes
            ),
            (None, None),
        )
        while new_day is None:
            year -= 1
            for month, day in self.days[::-1]:
                if (
                    day_exists(year, month, day)
                    and date(year, month, day) not in self.excludes
                ):
                    new_month = month
                    new_day = day
                    break
        return date(year, new_month, new_day)
