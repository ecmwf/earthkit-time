from datetime import date, datetime, time, timedelta
from typing import Iterable, Iterator, Tuple, Union

from earthkit.time.calendar import MonthInYear, Weekday, month_length


def parse_range(arg: str) -> Tuple[int, int]:
    """Convert a "start-end" step range to a tuple"""
    start, sep, end = arg.partition("-")
    if not sep:
        end = start
    try:
        return (int(start), int(end))
    except ValueError:
        raise ValueError(f"Invalid step range: {arg!r}")


def regular_ranges(
    start: int, end: int, width: int, interval: int
) -> Iterator[Tuple[int, int]]:
    """Iterate over regularly-spaced step ranges

    This generates ``(a, b)`` pairs where ``a`` is ``start``, ``start +
    interval``, ``start + 2 * interval``, ... and ``b = a + width``, such that
    the last pair satisfies ``b <= end``.

    Example
    -------
    >>> list(regular_ranges(24, 48, 12, 6))
    [(24, 36), (30, 42), (36, 48)]
    """
    for step in range(start, end - width + 1, interval):
        yield (step, step + width)


def expand_range(
    steprange: Union[str, Tuple[int, int]], interval: int, include_start: bool = True
) -> Iterable[int]:
    """Iterate over regularly-spaced steps within a range

    Examples
    --------
    >>> list(expand_range("0-24", 6))
    [0, 6, 12, 18, 24]
    >>> list(expand_range((48, 96), 24, include_start=False))
    [72, 96]
    """
    if isinstance(steprange, str):
        steprange = parse_range(steprange)
    start, end = steprange
    if not include_start:
        start += interval
    return range(start, end + 1, interval)


def hours_from_delta(delta: timedelta) -> int:
    """Convert a :class:`~datetime.timedelta` to a whole number of hours"""
    return round(delta.total_seconds() / 3600)


def _daily_shift(
    base: Union[datetime, time, int] = 0,
    daystart: Union[time, int] = 0,
) -> int:
    if isinstance(base, datetime):
        base = base.time()
    if isinstance(base, time):
        base = base.hour
    if isinstance(daystart, time):
        daystart = daystart.hour
    return (daystart - base) % 24


def range_from_day(
    day: int, base: Union[datetime, time, int] = 0, daystart: Union[time, int] = 0
) -> Tuple[int, int]:
    """Compute the step range corresponding to a given day

    Day 1 starts on the first time step with valid time ``daystart``.
    """
    shift = _daily_shift(base, daystart)
    start = shift + 24 * (day - 1)
    end = start + 24
    return (start, end)


def day_from_range(
    steprange: Tuple[int, int],
    base: Union[datetime, time, int] = 0,
    daystart: Union[time, int] = 0,
) -> int:
    """Compute the day number corresponding to the given step range

    This is the exact inverse of :func:`range_from_day`.
    """
    shift = _daily_shift(base, daystart)
    start, end = steprange
    if end - start != 24:
        raise ValueError(f"Range '{steprange[0]}-{steprange[1]}' is not one day long")
    day, rem = divmod((end - shift), 24)
    if rem != 0:
        raise ValueError(
            f"Range '{steprange[0]}-{steprange[1]}' does not align on a day"
        )
    return day


_WEEK_IN_HOURS = 7 * 24


def _weekly_shift(
    base: Union[date, datetime, time, Weekday, Tuple[Weekday, time], None] = None,
    weekstart: Union[Weekday, None] = None,
) -> int:
    if base is None:
        if weekstart is None:
            return 0
        raise ValueError("Cannot compute non-trivial week shift without a base time")

    if isinstance(base, Weekday):
        basewd = base
        basehour = 0
    elif isinstance(base, datetime):
        basewd = base.weekday()
        basehour = base.hour
    elif isinstance(base, date):
        basewd = base.weekday()
        basehour = 0
    elif isinstance(base, time):
        basewd = None
        basehour = base.hour
    elif isinstance(base, tuple):
        basewd, basetime = base
        assert isinstance(basewd, Weekday)
        assert isinstance(basetime, time)
        basehour = basetime.hour
    else:
        raise TypeError(f"Invalid type for `base`: {type(base)!r}")

    if weekstart is None:
        return (-basehour) % 24
    elif isinstance(weekstart, Weekday):
        if basewd is None:
            raise ValueError(
                "Cannot compute non-trivial week shift without a base week day"
            )
        shift = ((weekstart - basewd) % 7) * 24 - basehour
        if shift < 0:
            shift += _WEEK_IN_HOURS
        return shift
    else:
        raise TypeError(f"Invalid type for `weekstart`: {type(weekstart)!r}")


def range_from_week(
    week: int,
    base: Union[date, datetime, time, Weekday, Tuple[Weekday, time], None] = None,
    weekstart: Union[Weekday, None] = None,
) -> Tuple[int, int]:
    """Compute the step range corresponding to a given week

    If ``base`` is ``None``, ``weekstart`` must be ``None`` as well,
    corresponding to the first week starting at step 0. If ``base`` is a
    :class:`~datetime.time`, ``weekstart`` must be ``None``. If no time
    component is present in ``base``, it is assumed to be 00:00.

    If no week start is given, the first week is assumed to start on the first
    time step with valid time 00:00.

    Examples
    --------
    >>> from datetime import date, datetime, time
    >>> from earthkit.time.calendar import MONDAY, SUNDAY, THURSDAY
    >>> range_from_week(1)
    (0, 168)
    >>> range_from_week(2, time(12))
    (180, 348)
    >>> range_from_week(1, THURSDAY, MONDAY)
    (96, 264)
    >>> range_from_week(1, (THURSDAY, time(12)), MONDAY)
    (84, 252)
    >>> range_from_week(3, date(2023, 11, 10), SUNDAY)  # 2023-11-10 is a Friday
    (384, 552)
    >>> range_from_week(3, datetime(2023, 11, 10, 6), SUNDAY)
    (378, 546)
    """
    shift = _weekly_shift(base, weekstart)
    start = shift + _WEEK_IN_HOURS * (week - 1)
    end = start + _WEEK_IN_HOURS
    return (start, end)


def week_from_range(
    steprange: Tuple[int, int],
    base: Union[date, datetime, time, Weekday, Tuple[Weekday, time], None] = None,
    weekstart: Union[Weekday, None] = None,
) -> int:
    """Compute the week number corresponding to the given step range

    This is the exact inverse of :func:`range_from_week`.
    """
    shift = _weekly_shift(base, weekstart)
    start, end = steprange
    if end - start != _WEEK_IN_HOURS:
        raise ValueError(f"Range '{steprange[0]}-{steprange[1]}' is not one week long")
    week, rem = divmod((end - shift), _WEEK_IN_HOURS)
    if rem != 0:
        raise ValueError(
            f"Range '{steprange[0]}-{steprange[1]}' does not align on a week"
        )
    return week


def _month_to_date(
    arg: Union[date, MonthInYear, Tuple[int, int]], day: int = 1
) -> date:
    if isinstance(arg, date):
        return arg
    if isinstance(arg, MonthInYear):
        return date(arg.year, arg.month, day)
    if isinstance(arg, tuple):
        year, month = arg
        return date(year, month, day)
    raise TypeError(f"Cannot convert {type(arg)} to a date")


def startdate_from_month(
    month: int,
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int = 1,
) -> date:
    """Compute the date of the first day of a forecast month

    Parameters
    ----------
    month: int
        Forecast month (first month has index 1)
    base: :class:`~datetime.date`, :class:`~earthkit.time.calendar.MonthInYear`, ``(year, month)`` tuple
        Forecast base time. The first day is assumed to be 1 if not provided.
    mstart: int
        Starting day for the month
    """
    base = _month_to_date(base, mstart)
    if base.day > mstart:
        month += 1
    dyear, vmonth = divmod(base.month + month - 2, 12)
    vmonth += 1
    return base.replace(year=base.year + dyear, month=vmonth, day=mstart)


def month_from_startdate(
    base: Union[date, MonthInYear, Tuple[int, int]],
    start: Union[date, MonthInYear, Tuple[int, int]],
) -> int:
    """Compute the forecast month starting on the given date

    The first month has number 1

    Parameters
    ----------
    base: :class:`~datetime.date`, :class:`~earthkit.time.calendar.MonthInYear`, ``(year, month)`` tuple
        Forecast base time. The first day is assumed to be 1 if not provided.
    start: :class:`~datetime.date`, :class:`~earthkit.time.calendar.MonthInYear`, ``(year, month)`` tuple
        Month start date. The first day is assumed to be 1 if not provided.
    """
    mstart = start.day if isinstance(start, date) else 1
    base = _month_to_date(base, mstart)
    start = _month_to_date(start, mstart)
    dyear = start.year - base.year
    dmonth = start.month - base.month
    if base.day > start.day:
        dmonth -= 1
    return dyear * 12 + dmonth + 1


def range_from_month(
    month: int,
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int = 1,
) -> Tuple[int, int]:
    """Compute the step range corresponding to a forecast month

    Parameters
    ----------
    month: int
        Forecast month (first month has index 1)
    base: :class:`~datetime.date`, :class:`~earthkit.time.calendar.MonthInYear`, ``(year, month)`` tuple
        Forecast base date. The first day is assumed to be 1 if not provided.
    mstart: int
        Starting day for the month

    Examples
    --------
    >>> from datetime import date
    >>> range_from_month(1, (2026, 1))
    (0, 744)
    >>> range_from_month(2, date(2025, 1, 1))
    (744, 1416)
    >>> range_from_month(4, date(2023, 1, 15))
    (2544, 3288)
    >>> range_from_month(5, date(2022, 1, 15), 15)
    (2880, 3624)
    """
    base = _month_to_date(base, mstart)
    valid = startdate_from_month(month, base, mstart)
    start = hours_from_delta(valid - base)
    end = start + month_length(valid.year, valid.month) * 24
    return (start, end)


def month_from_range(
    steprange: Tuple[int, int],
    base: Union[date, MonthInYear, Tuple[int, int]],
    mstart: int = 1,
) -> int:
    """Compute the forecast month corresponding to the given step range

    This is the exact inverse of :func:`range_from_month`.
    """
    base = _month_to_date(base, mstart)
    startstep, endstep = steprange
    start = base + timedelta(hours=startstep)
    if start.day != mstart:
        raise ValueError(
            f"Range '{steprange[0]}-{steprange[1]}' does not align on a forecast month"
        )
    end = base + timedelta(hours=endstep)
    if end.day != start.day:
        raise ValueError(f"Range '{steprange[0]}-{steprange[1]}' is not one month long")
    return month_from_startdate(base, start)
