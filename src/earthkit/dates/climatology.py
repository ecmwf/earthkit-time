"""Date utilities to build a climatology"""

from datetime import date
from typing import Iterator, Union


def date_range(
    reference: date,
    start: Union[date, int],
    end: Union[date, int],
    recurrence: str = "yearly",
    include_endpoint: bool = True,
) -> Iterator[date]:
    """Generate a sequence of dates following a recurrence pattern

    If the reference date is February 29th on a leap year, it will be replaced
    by February 28th for every year in the output.

    Parameters
    ----------
    reference: date
        Reference date setting the fixed part in the sequence (e.g., month and day
        for a yearly recurrence)
    start: date or int
        Start of the period. Either a full date or a meaningful identifier (e.g.
        year for a yearly recurrence)
    end: date or int
        End of the period. Included in the sequence unless ``include_endpoint`` is
        ``False``
    recurrence: "yearly"
        Type of recurrence
    include_endpoint: bool
        If ``False``, do not include the end in the sequence

    Returns
    -------
    date iterator
        Sequence of dates

    Examples
    --------
    >>> list(date_range(date(2020, 4, 12), 1999, 2002))
    [datetime.date(1999, 4, 12), datetime.date(2000, 4, 12), datetime.date(2001, 4, 12), datetime.date(2002, 4, 12)]
    >>> list(date_range(date(2020, 4, 12), 1999, 2002, include_endpoint=False))
    [datetime.date(1999, 4, 12), datetime.date(2000, 4, 12), datetime.date(2001, 4, 12)]
    >>> list(date_range(date(2014, 8, 23), date(2010, 8, 16), date(2012, 8, 1)))
    [datetime.date(2010, 8, 23), datetime.date(2011, 8, 23)]
    """

    _known_recurrences = ["yearly"]
    if recurrence not in _known_recurrences:
        known = ", ".join(_known_recurrences)
        raise ValueError(f"Unknown recurrence {recurrence!r}, expected one of: {known}")

    if recurrence == "yearly":
        if reference.month == 2 and reference.day == 29:
            reference = reference.replace(day=28)

        if isinstance(start, date):
            rstart = start.replace(month=reference.month, day=reference.day)
            start = start.year if start <= rstart else start.year + 1

        if isinstance(end, date):
            rend = end.replace(month=reference.month, day=reference.day)
            end = (
                end.year
                if end > rend or (end == rend and include_endpoint)
                else end.year - 1
            )
        elif not include_endpoint:
            end -= 1

        for year in range(start, end + 1):
            yield reference.replace(year=year)
