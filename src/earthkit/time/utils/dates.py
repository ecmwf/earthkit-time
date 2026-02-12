# (C) Copyright 2024 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime
import re

from dateutil.parser import isoparse
from dateutil.parser import parse
import numpy as np
from typing import Any

VALID_DATE_PATTERN = re.compile(r"\d\d\d\d-?\d\d-?\d\d([T\s]\d\d:\d\d(:\d\d)?)?Z?")


def str_to_datetime(value: str) -> datetime.datetime:
    """Convert a string to a datetime object.

    Parameters
    ----------
    value : str
        The string representation of a datetime.

    Returns
    -------
    datetime.datetime
        The parsed datetime object.

    """
    if not VALID_DATE_PATTERN.match(value):
        raise ValueError(f"Invalid datetime '{value}'")

    # Try to parse the date using different methods
    try:
        return datetime.datetime.fromisoformat(value)
    except Exception:
        pass

    try:
        return isoparse(value)
    except ValueError:
        pass

    return parse(value)


def str_to_datetime_list(value: str) -> list:
    """Convert a MARS-style list to list of datetime objects.

    Parameters
    ----------
    value : str
        MARS-style date list in the format of "start_date/TO/end_date[/BY/step]".
        "BY/step" is optional and defaults to 1 (day). The expression is case-insensitive.
        Some examples:

         - "2023-05-01/TO/2023-05-06"
         - "20230501/TO/20230506/BY/1"
         - "2023-05-01/TO/2023-05-06/BY/2"

    Returns
    -------
    list of datetime.datetime
        List of datetime objects representing the dates in the MARS-style list.

    """
    # MARS style lists
    bits = value.split("/")
    if len(bits) == 3 and bits[1].lower() == "to":
        return mars_like_date_list(str_to_datetime(bits[0]), str_to_datetime(bits[2]), 1)

    if len(bits) == 5 and bits[1].lower() == "to" and bits[3].lower() == "by":
        return mars_like_date_list(str_to_datetime(bits[0]), str_to_datetime(bits[2]), int(bits[4]))

    return [str_to_datetime(d) for d in bits]


def int_to_datetime(value: int) -> datetime.datetime:
    """Convert an integer to a datetime object.

    Parameters
    ----------
    value : int
        The integer representation of a date, e.g. 20231001 for 1st October 2023,
        or a negative integer representing days before today. Zero means today.
        The time is set to midnight (00:00:00).

    Returns
    -------
    datetime.datetime
        The converted datetime object.

    """
    if value <= 0:
        date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=value)
        return datetime.datetime(date.year, date.month, date.day)
    else:
        return datetime.datetime(value // 10000, value % 10000 // 100, value % 100)


def to_datetime(dt: Any, wrapper=None) -> datetime.datetime:
    """Convert various types to a datetime object.

    Parameters
    ----------
    dt : Any
        The input value to convert.
    wrapper : callable, optional
        A callable that can be used to wrap the input value to
        an object that has a `to_datetime` method.

    Returns
    -------
    datetime.datetime

    """
    if isinstance(dt, datetime.datetime):
        return dt

    if isinstance(dt, datetime.date):
        return datetime.datetime(dt.year, dt.month, dt.day)

    if hasattr(dt, "dtype") and np.issubdtype(dt.dtype, np.datetime64):
        return numpy_datetime_to_datetime(dt)

    if isinstance(dt, np.int64):
        dt = int(dt)

    if isinstance(dt, str):
        return str_to_datetime(dt)

    if isinstance(dt, int):
        return int_to_datetime(dt)

    if callable(wrapper):
        dt = wrapper(dt)
        return to_datetime(dt.to_datetime())

    return None


def mars_like_date_list(start: datetime.datetime, end: datetime.datetime, by: int) -> list:
    """Return a list of datetime objects for an interval.

    Parameters
    ----------
    start : datetime.datetime
        Start datetime object
    end : datetime.datetime
        End datetime object
    by : int
        Days between each datetime object

    Returns
    -------
    list of datetime.datetime
    """
    assert by > 0, by
    assert end >= start
    result = []
    while start <= end:
        result.append(start)
        start = start + datetime.timedelta(days=by)
    return result


def to_datetime_list(datetimes, wrapper=None) -> list:  # noqa C901
    """Convert various types to a list of datetime objects.

    Parameters
    ----------
    datetimes : Any
        The input value to convert. It can be a single object that can be converted to
        a datetime, a list these or string in MARS-style date list format.
    wrapper : callable, optional
        A callable that can be used to wrap the input value to
        an object that has a `to_datetime_list` method.

    Returns
    -------
    list of datetime.datetime
    """
    if isinstance(datetimes, (datetime.datetime, np.datetime64)):
        return to_datetime_list([datetimes])

    if isinstance(datetimes, (list, tuple)):
        if len(datetimes) == 3 and isinstance(datetimes[1], str) and datetimes[1].lower() == "to":
            return mars_like_date_list(to_datetime(datetimes[0]), to_datetime(datetimes[2]), 1)

        if (
            len(datetimes) == 5
            and isinstance(datetimes[1], str)
            and isinstance(datetimes[3], str)
            and datetimes[1].lower() == "to"
            and datetimes[3].lower() == "by"
        ):
            return mars_like_date_list(
                to_datetime(datetimes[0]), to_datetime(datetimes[2]), int(datetimes[4])
            )

        return [to_datetime(x) for x in datetimes]

    if isinstance(datetimes, int):
        return to_datetime_list([int_to_datetime(datetimes)])

    if isinstance(datetimes, str):
        return to_datetime_list(str_to_datetime_list(datetimes))

    if callable(wrapper):
        datetimes = wrapper(datetimes)
        return to_datetime_list(datetimes.to_datetime_list())

    return None


def to_date_list(obj) -> list:
    return sorted(set(to_datetime_list(obj)))


def to_time(dt) -> datetime.time:
    """Convert various types to a datetime.time object.

    Parameters
    ----------
    dt : Any
        The input value to convert.

    Returns
    -------
    datetime.time
    """
    if isinstance(dt, float):
        dt = int(dt)

    if isinstance(dt, str):
        if len(dt) <= 4:
            dt = int(dt)
        else:
            return to_datetime(dt).time()

    if isinstance(dt, np.int64):
        dt = int(dt)

    if isinstance(dt, int):
        if dt >= 2400:
            return to_datetime(dt).time()
        else:
            h = int(dt / 100)
            m = dt % 100
            return datetime.time(hour=h, minute=m)

    if isinstance(dt, datetime.time):
        return dt

    if isinstance(dt, datetime.datetime):
        return dt.time()

    if isinstance(dt, datetime.date):
        return dt.time()

    if hasattr(dt, "dtype") and np.issubdtype(dt.dtype, np.datetime64):
        return numpy_datetime_to_datetime(dt).time()

    if hasattr(dt, "dtype") and np.issubdtype(dt.dtype, np.timedelta64):
        dt = numpy_timedelta_to_timedelta(dt)

    if isinstance(dt, datetime.timedelta):
        return datetime.time(
            hour=int(dt.total_seconds()) // 3600,
            minute=int(dt.total_seconds()) // 60 % 60,
            second=int(dt.total_seconds()) % 60,
        )

    raise ValueError(f"Failed to convert time={dt} of type={type(dt)} to datetime.time")


def to_time_list(times) -> list:
    """Convert various types to a list of datetime.time objects.

    Parameters
    ----------
    times : Any
        The input value to convert.

    Returns
    -------
    list of datetime.time
        A list of datetime.time objects representing the times in the input.
    """
    if not isinstance(times, (list, tuple)):
        return to_time_list([times])
    return [to_time(x) for x in times]


def to_timedelta(td) -> datetime.timedelta:
    """Convert various types to a datetime.timedelta object.

    Parameters
    ----------
    td : Any
        The input value to convert.

    Returns
    -------
    datetime.timedelta
        A datetime.timedelta object representing the time duration.

    Raises
    ------
    ValueError
        If the input cannot be converted to a datetime.timedelta object.
    """
    if isinstance(td, int):
        return datetime.timedelta(hours=td)

    if isinstance(td, datetime.time):
        return datetime.timedelta(hours=td.hour, minutes=td.minute, seconds=td.second)

    if isinstance(td, datetime.timedelta):
        return td

    if not isinstance(td, str) and np.issubdtype(td, np.timedelta64):
        return numpy_timedelta_to_timedelta(td)

    # last resort: assume it is an ecCodes step format
    # and convert it to a timedelta
    from .grib import grib_step_to_timedelta

    return grib_step_to_timedelta(td, raise_on_error=True)


def numpy_timedelta_to_timedelta(td) -> datetime.timedelta:
    """Convert a numpy timedelta64 object to a datetime.timedelta object.

    Parameters
    ----------
    td : numpy.timedelta64
        The numpy timedelta64 object to convert.

    Returns
    -------
    datetime.timedelta
        The converted datetime.timedelta object.

    """
    td = td.astype("timedelta64[s]").astype(int)
    return datetime.timedelta(seconds=int(td))


def numpy_datetime_to_datetime(dt) -> datetime.datetime:
    """Convert a numpy datetime64 object to a datetime.datetime object.

    Parameters
    ----------
    dt : numpy.datetime64
        The numpy datetime64 object to convert.

    Returns
    -------
    datetime.datetime
        The converted datetime.datetime object.

    """
    dt = dt.astype("datetime64[s]").astype(int)
    return datetime.datetime.fromtimestamp(int(dt), datetime.timezone.utc).replace(tzinfo=None)


def timedeltas_to_int(td) -> tuple:
    """Convert a list of timedeltas to a list of integers and the resolution.

    Parameters
    ----------
    td : list or tuple of datetime.timedelta
        A list or tuple of datetime.timedelta objects to convert.

    Returns
    -------
    tuple
        A tuple containing:
        - A list of integers in the units of the resolution
        - The resolution as a datetime.timedelta object

    """

    def _gcd(td):
        if td.total_seconds() % 3600 == 0:
            return datetime.timedelta(hours=1)
        if td.total_seconds() % 60 == 0:
            return datetime.timedelta(minutes=1)
        if td.microseconds == 0:
            return datetime.timedelta(seconds=1)
        else:
            return td.resolution

    if not isinstance(td, (list, tuple)):
        td = [td]

    resolution = min([_gcd(x) for x in td])
    resolution_secs = int(resolution.total_seconds())
    return [int(x.total_seconds() / resolution_secs) for x in td], resolution
