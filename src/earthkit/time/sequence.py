import os.path
from abc import ABC, abstractmethod
from datetime import date, timedelta
from typing import Container, Dict, Iterable, Iterator, Optional, Tuple, Type, Union

from .calendar import (
    MonthInYear,
    Weekday,
    day_exists,
    parse_date,
    parse_mmdd,
    to_weekday,
)
from .data import load_yaml


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

    def nearest(self, reference: date, resolve: str = "previous") -> date:
        """Return the date closest to ``reference`` in the sequence.
        In case this is ambiguous, ``resolve`` defines which date to use
        (``"previous"`` or ``"next"``).
        """
        if resolve not in ["previous", "next"]:
            raise ValueError('`resolve` must be either "previous" or "next"')
        before = self.previous(reference, strict=False)
        after = self.next(reference, strict=False)
        delta_b = reference - before
        delta_a = after - reference
        if delta_b < delta_a:
            return before
        elif delta_b > delta_a:
            return after
        elif resolve == "previous":
            return before
        else:
            return after

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

    @classmethod
    @abstractmethod
    def _from_dict(cls, seq_dict: dict) -> "Sequence":
        """Create a specific sequence from the given dictionary

        Dictionary contents can vary depending on the sequence. Frequent items are:
        * days: list of recurring days
        * excludes: specification of which days to skip
        """
        raise NotImplementedError

    _known_types: Dict[str, Type["Sequence"]] = {}

    @classmethod
    def _register_sequence(cls, name: str, class_: Type["Sequence"]):
        assert name not in cls._known_types
        cls._known_types[name] = class_

    @classmethod
    def __init_subclass__(cls, /, seqname: Optional[str] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if seqname is not None:
            Sequence._register_sequence(seqname, cls)

    @classmethod
    def from_dict(cls, seq_dict: dict) -> "Sequence":
        """Create a sequence from the given dictionary

        The type of sequence is specified by the ``type`` key, and must match
        one of the known sequences, e.g. ``daily``, ``weekly``, ``monthly``,
        ``yearly``.

        Dictionary contents can vary depending on the sequence. Frequent items are:
        * days: list of recurring days
        * excludes: specification of which days to skip

        Raises `ValueError` if the type is unknown
        """
        if "type" not in seq_dict:
            raise ValueError("Sequence dictionary must contain `type` key")
        type_ = seq_dict["type"]
        if type_ not in cls._known_types:
            raise ValueError(f"Unknown type {type_!r}")
        return cls._known_types[type_]._from_dict(seq_dict)

    @classmethod
    def from_resource(cls, name: str) -> "Sequence":
        """Load a sequence from a resource file

        ``name`` should be either the name of a known sequence (in
        ``earthkit.time.data.sequences`` or ``EARTHKIT_TIME_SEQ_PATH``,
        without the extension), or the path to a YAML file

        Raises `FileNotFoundError` if no corresponding resource is found
        """
        path = name if os.path.isfile(name) else None
        seq_dict = load_yaml(
            f"sequences/{name}.yaml", path, env_path="EARTHKIT_TIME_SEQ_PATH"
        )
        if not isinstance(seq_dict, dict):
            raise ValueError("Invalid resource file")
        return cls.from_dict(seq_dict)


class DailySequence(Sequence, seqname="daily"):
    """Sequence of consecutive dates

    Any day number (in the month) present in ``excludes`` will be skipped

    Can be created from a `dict` with items:
    * ``type``: ``"daily"``
    * ``excludes``: (list of int, optional) days of the month to exclude
    """

    def __init__(self, excludes: Container[int] = set()):
        self.excludes = excludes

    def __contains__(self, reference: date) -> bool:
        return reference.day not in self.excludes

    def __repr__(self) -> str:
        return f"DailySequence(excludes={self.excludes!r})"

    @classmethod
    def _from_dict(cls, seq_dict: dict) -> Sequence:
        return cls(excludes=set(seq_dict.get("excludes", set())))


class WeeklySequence(Sequence, seqname="weekly"):
    """Sequence of dates happening on given days of each week

    Can be created from a `dict` with items:
    * ``type``: ``"weekly"``
    * ``days``: (int, str, list of int, list of str) days of the week, either
      numeric (0 = Monday, ..., 6 = Sunday) or unambiguous prefixes of names
      (e.g. ``"M"``, ``"tue"``, ``"Friday"``)
    """

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

    @classmethod
    def _from_dict(cls, seq_dict: dict) -> Sequence:
        if "days" not in seq_dict:
            raise ValueError("Weekly sequence must provide `days`")
        days = seq_dict["days"]
        if isinstance(days, (int, str)):
            days = [to_weekday(days)]
        else:
            days = [to_weekday(day) for day in days]
        return cls(days)


class MonthlySequence(Sequence, seqname="monthly"):
    """Sequence of dates happening on given days of each month

    Any ``(month, day)`` tuple present in ``excludes`` will be skipped

    Can be created from a `dict` with items:
    * ``type``: ``"monthly"``
    * ``days``: (int, list of int) days of the month (1-31)
    * ``excludes``: (list of pairs of int, list of str, optional) days of the
      year to exclude, either in (month, day) or in "MMDD" form
    """

    def __init__(
        self,
        days: Union[int, Iterable[int]],
        excludes: Container[Tuple[int, int]] = set(),
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

    @classmethod
    def _from_dict(cls, seq_dict: dict) -> Sequence:
        if "days" not in seq_dict:
            raise ValueError("Monthly sequence must provide `days`")
        excludes = {parse_mmdd(exc) for exc in seq_dict.get("excludes", set())}
        return cls(seq_dict["days"], excludes=excludes)


class YearlySequence(Sequence, seqname="yearly"):
    """Sequence of dates happening on given days of each year (in (month, day) format)

    Can be created from a `dict` with items:
    * ``type``: ``"yearly"``
    * ``days``: (str, pair of int, list of str, list of pairs of int) days of the year
      either in "MMDD" or in (month, day) form (1-12, 1-31)
    * ``excludes``: (list of str, list of triples of int) dates to exclude,
      either in "YYYYMMDD" or in (year, month, day) form
    """

    def __init__(
        self,
        days: Union[Tuple[int, int], Iterable[Tuple[int, int]]],
        excludes: Container[date] = set(),
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

    @classmethod
    def _from_dict(cls, seq_dict: dict) -> Sequence:
        if "days" not in seq_dict:
            raise ValueError("Yearly sequence must provide `days`")
        days = seq_dict["days"]
        if isinstance(days, str) or isinstance(days[0], int):
            days = [parse_mmdd(days)]
        else:
            days = [parse_mmdd(day) for day in days]
        excludes = {parse_date(exc) for exc in seq_dict.get("excludes", set())}
        return cls(days, excludes=excludes)
