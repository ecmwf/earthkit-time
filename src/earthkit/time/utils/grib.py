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
from typing import Any

import numpy as np

from .dates import to_datetime, to_time, to_timedelta

ECC_SECONDS_FACTORS = {"s": 1, "m": 60, "h": 3600}
NUM_STEP_PATTERN = re.compile(r"\d+")
SUFFIX_STEP_PATTERN = re.compile(r"\d+[a-zA-Z]{1}")


def date_to_grib(date: Any) -> int:
    """Convert a date to an integer as used in GRIB.

    Parameters
    ----------
    date : Any
        The input value to convert. It can be a datetime object, a date object,
        a string, an integer or a numpy datetime64 object.

    Returns
    -------
    int
        The date represented as an integer in the format YYYYMMDD.
    """
    try:
        date = to_datetime(date)
        if isinstance(date, datetime.datetime):
            return int(date.year * 10000 + date.month * 100 + date.day)
    except Exception as e:
        raise ValueError(f"Cannot convert date={date} of type={type(date)} to grib metadata. {e}")


def time_to_grib(time: Any) -> int:
    """Convert a time to an integer as used in GRIB.

    Parameters
    ----------
    time : Any
        The input value to convert.

    Returns
    -------
    int
        The time represented as an integer in GRIB. The format is
        HH[MM].
    """
    time = to_time(time)

    if isinstance(time, datetime.time):
        return time.hour * 100 + time.minute
    try:
        time = int(time)
        if time < 100:
            time = time * 100
    except ValueError:
        pass

    return time


def grib_step_to_timedelta(step, raise_on_error=True) -> datetime.timedelta:
    """Convert various types to a datetime.timedelta object.

    Parameters
    ----------
    step : Any
        The input value to convert. It can be an integer representing hours,
        a datetime.time object, a string in the format of "HH", "HHm", or "HHs",
        a datetime.timedelta object, or a numpy timedelta64 object.

    Returns
    -------
    datetime.timedelta
        A datetime.timedelta object representing the time duration.

    Raises
    ------
    ValueError
        If the input cannot be converted to a datetime.timedelta object.
    """
    if isinstance(step, int):
        return datetime.timedelta(hours=step)

    # eccodes step format
    # TODO: make it work for all the ecCodes step formats
    if isinstance(step, str):
        if re.fullmatch(NUM_STEP_PATTERN, step):
            return datetime.timedelta(hours=int(step))

        if re.fullmatch(SUFFIX_STEP_PATTERN, step):
            factor = ECC_SECONDS_FACTORS.get(step[-1], None)
            if factor is None:
                if raise_on_error:
                    raise ValueError(f"Unsupported ecCodes step units in step: {step}")
                return None
            return datetime.timedelta(seconds=int(step[:-1]) * factor)

    if raise_on_error:
        raise ValueError(f"Failed to convert {step=} type={type(step)} to timedelta")
    else:
        return None


def step_to_grib(step: Any) -> int:
    """Convert a step to the format used in GRIB."""
    if isinstance(step, (int, str)):
        return step
    elif isinstance(step, np.int64):
        return int(step)

    step = to_timedelta(step)

    if isinstance(step, datetime.timedelta):
        hours, minutes, seconds = (
            int(step.total_seconds() // 3600),
            int(step.seconds // 60 % 60),
            int(step.seconds % 60),
        )
        if seconds == 0:
            if minutes == 0:
                return hours
            else:
                return f"{hours*60}{minutes}m"
        else:
            return f"{int(step.total_seconds())}s"

    raise ValueError(f"Cannot convert step={step} of type={type(step)} to grib metadata")


def datetime_to_grib(dt: Any) -> tuple:
    """Convert a datetime to a tuple of date and time as used in GRIB."""
    dt = to_datetime(dt)
    date = int(dt.strftime("%Y%m%d"))
    time = dt.hour * 100 + dt.minute
    return date, time


def grib_date_and_time_to_datetime(date: int, time: int) -> datetime.datetime:
    """Convert date and time from GRIB format to a datetime object."""
    date = int(date)
    time = int(time)

    return datetime.datetime(
        date // 10000,
        date % 10000 // 100,
        date % 100,
        time // 100,
        time % 100,
    )
