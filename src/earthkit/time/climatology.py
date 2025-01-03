"""Date utilities to build a climatology"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator, Union

from .sequence import Sequence, YearlySequence
from .utilities import merge_sorted


@dataclass
class RelativeYear:
    """Wrapper for a year intended to be relative to a reference"""

    value: int

    def relative_to(self, reference: Union[date, int]) -> int:
        if isinstance(reference, date):
            reference = reference.year
        return reference + self.value


def date_range(
    reference: date,
    start: Union[date, int, RelativeYear],
    end: Union[date, int, RelativeYear],
    recurrence: str = "yearly",
    include_endpoint: bool = True,
) -> Iterator[date]:
    """Generate a sequence of dates following a recurrence pattern

    If the reference date is February 29th on a leap year, it will be replaced
    by February 28th for every year in the output.

    Parameters
    ----------
    reference: :class:`datetime.date`
        Reference date setting the fixed part in the sequence (e.g., month and day
        for a yearly recurrence)
    start: :class:`datetime.date`, int, or :class:`RelativeYear`
        Start of the period. Either a full date or a meaningful identifier (e.g.
        year for a yearly recurrence)
    end: :class:`datetime.date`, int, or :class:`RelativeYear`
        End of the period. Included in the sequence unless ``include_endpoint`` is
        ``False``
    recurrence: "yearly"
        Type of recurrence
    include_endpoint: bool
        If ``False``, do not include the end in the sequence

    Returns
    -------
    :class:`datetime.date` iterator
        Sequence of dates

    Examples
    --------
    >>> list(date_range(date(2020, 4, 12), 1999, 2002))
    [datetime.date(1999, 4, 12), datetime.date(2000, 4, 12), datetime.date(2001, 4, 12), datetime.date(2002, 4, 12)]
    >>> list(date_range(date(2020, 4, 12), 1999, 2002, include_endpoint=False))
    [datetime.date(1999, 4, 12), datetime.date(2000, 4, 12), datetime.date(2001, 4, 12)]
    >>> list(date_range(date(2014, 8, 23), date(2010, 8, 16), date(2012, 8, 1)))
    [datetime.date(2010, 8, 23), datetime.date(2011, 8, 23)]
    >>> list(date_range(date(2014, 8, 23), RelativeYear(-3), RelativeYear(-1)))
    [datetime.date(2011, 8, 23), datetime.date(2012, 8, 23), datetime.date(2013, 8, 23)]
    """

    _known_recurrences = ["yearly"]
    if recurrence not in _known_recurrences:
        known = ", ".join(_known_recurrences)
        raise ValueError(f"Unknown recurrence {recurrence!r}, expected one of: {known}")

    if recurrence == "yearly":
        if reference.month == 2 and reference.day == 29:
            reference = reference.replace(day=28)

        if isinstance(start, RelativeYear):
            start = start.relative_to(reference)
        if not isinstance(start, date):
            start = reference.replace(year=start)

        if isinstance(end, RelativeYear):
            end = end.relative_to(reference)
        if not isinstance(end, date):
            end = reference.replace(year=end)

        seq = YearlySequence((reference.month, reference.day))
        yield from seq.range(start, end, include_end=include_endpoint)


def model_climate_dates(
    reference: date,
    start: Union[date, int, RelativeYear],
    end: Union[date, int, RelativeYear],
    before: Union[timedelta, int],
    after: Union[timedelta, int],
    sequence: Sequence,
) -> Iterator[date]:
    """Generate a set of dates for a model climate

    The set is created by combining yearly dates between ``start`` and ``end``,
    for each date between ``reference - before`` and ``reference + after``. If
    any of these dates is February 29th, the whole corresponing sequence will
    use February 28th instead.

    Parameters
    ----------
    reference: :class:`datetime.date`
        Reference date for the climate
    start: :class:`datetime.date`, int, or :class:`RelativeYear`
        Start of the climatological period. Either a full date or a year
    end: :class:`datetime.date`, int, or :class:`RelativeYear`
        End of the climatological period. Either a full date or a year
    before: :class:`datetime.timedelta` or int
        Cut-off before the reference date. Either a timedelta or a number of
        days
    after: :class:`datetime.timedelta` or int
        Cut-off after the reference date. Either a timedelta or a number of days
    sequence: :class:`earthkit.time.sequence.Sequence`
        Sequence of available dates in the reference set

    Returns
    -------
    :class:`datetime.date` iterator
        Sequence of dates

    Examples
    --------
    >>> from earthkit.time.calendar import MONDAY, THURSDAY
    >>> from earthkit.time import MonthlySequence, Sequence, WeeklySequence
    >>> sequence = WeeklySequence([MONDAY, THURSDAY])
    >>> [f"{d:%Y%m%d}" for d in model_climate_dates(date(2024, 2, 12), 2020, 2023, 7, 7, sequence)]
    ... # doctest: +NORMALIZE_WHITESPACE
    ['20200205', '20200208', '20200212', '20200215', '20200219',
     '20210205', '20210208', '20210212', '20210215', '20210219',
     '20220205', '20220208', '20220212', '20220215', '20220219',
     '20230205', '20230208', '20230212', '20230215', '20230219']
    >>> sequence = MonthlySequence(range(1, 32, 2), excludes=[(2, 29)])
    >>> [f"{d:%Y%m%d}" for d in model_climate_dates(date(2024, 2, 12), 2020, 2023, 7, 7, sequence)]
    ... # doctest: +NORMALIZE_WHITESPACE
    ['20200205', '20200207', '20200209', '20200211', '20200213', '20200215', '20200217', '20200219',
     '20210205', '20210207', '20210209', '20210211', '20210213', '20210215', '20210217', '20210219',
     '20220205', '20220207', '20220209', '20220211', '20220213', '20220215', '20220217', '20220219',
     '20230205', '20230207', '20230209', '20230211', '20230213', '20230215', '20230217', '20230219']
    >>> sequence = Sequence.from_resource("ecmwf-2days")
    >>> [f"{d:%Y%m%d}" for d in model_climate_dates(
    ...     date(2024, 12, 31), RelativeYear(-3), RelativeYear(-1), 2, 2, sequence
    ... )]
    ['20211229', '20211231', '20220101', '20221229', '20221231', '20230101', '20231229', '20231231', '20240101']
    """
    if not isinstance(before, timedelta):
        before = timedelta(days=before)
    if not isinstance(after, timedelta):
        after = timedelta(days=after)
    yield from merge_sorted(
        date_range(d, start, end)
        for d in sequence.range(reference - before, reference + after)
    )
