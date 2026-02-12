#!/usr/bin/env python3

# (C) Copyright 2020 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.
#

import datetime

import numpy as np
import pytest

from earthkit.time.utils.grib import date_to_grib
from earthkit.time.utils.grib import datetime_to_grib
from earthkit.time.utils.grib import step_to_grib
from earthkit.time.utils.grib import time_to_grib
from earthkit.time.utils.grib import grib_step_to_timedelta
from earthkit.time.utils.grib import grib_date_and_time_to_datetime


@pytest.mark.parametrize(
    "d,expected_value,error",
    [
        (20020502, 20020502, None),
        (np.int64(20020502), 20020502, None),
        ("20020502", 20020502, None),
        ("2002-05-02", 20020502, None),
        ("2002-05-02T00", 20020502, None),
        ("2002-05-02T00Z", 20020502, None),
        ("2002-05-02T06", 20020502, None),
        ("2002-05-02T06:11", 20020502, None),
        ("2002-05-02T06:11:03", 20020502, None),
        (datetime.datetime(2002, 5, 2, 6, 11, 3), 20020502, None),
        (np.datetime64("2002-05-02"), 20020502, None),
        (np.datetime64(0, "Y"), 19700101, None),
    ],
)
def test_date_to_grib(d, expected_value, error):
    if error is None:
        assert date_to_grib(d) == expected_value
    else:
        with pytest.raises(error):
            date_to_grib(d)


@pytest.mark.parametrize(
    "d,expected_value,error",
    [
        (0, 0, None),
        (6, 6, None),
        (12, 12, None),
        (600, 600, None),
        (1200, 1200, None),
        (1230, 1230, None),
        (np.int64(0), 0, None),
        (np.int64(6), 6, None),
        (np.int64(12), 12, None),
        (np.int64(600), 600, None),
        (np.int64(1200), 1200, None),
        (np.int64(1230), 1230, None),
        ("0", 0, None),
        ("6", 6, None),
        ("12", 12, None),
        ("600", 600, None),
        ("1200", 1200, None),
        ("1230", 1230, None),
        (datetime.timedelta(minutes=0), 0, None),
        (datetime.timedelta(minutes=6), 6, None),
        (datetime.timedelta(hours=0), 0, None),
        (datetime.timedelta(hours=6), 600, None),
        (datetime.timedelta(hours=12), 1200, None),
        (datetime.timedelta(hours=12, minutes=6), 1206, None),
        (datetime.timedelta(hours=120, seconds=2), None, ValueError),
        (np.timedelta64(0, "m"), 0, None),
        (np.timedelta64(6, "m"), 6, None),
        (np.timedelta64(0, "h"), 0, None),
        (np.timedelta64(6, "h"), 600, None),
        (np.timedelta64(12, "h"), 1200, None),
        (np.timedelta64(12 * 60 + 30, "m"), 1230, None),
    ],
)
def test_time_to_grib(d, expected_value, error):
    if error is None:
        assert time_to_grib(d) == expected_value
    else:
        with pytest.raises(error):
            time_to_grib(d)


@pytest.mark.parametrize(
    "step,expected_value,error",
    [
        (0, 0, None),
        (6, 6, None),
        (12, 12, None),
        (120, 120, None),
        ("0h", "0h", None),
        ("6h", "6h", None),
        ("12h", "12h", None),
        ("120h", "120h", None),
        ("6m", "6m", None),
        ("6s", "6s", None),
        (np.timedelta64(6, "h"), 6, None),
        (np.timedelta64(6 * 3600 * 1000, "ms"), 6, None),
        (np.timedelta64(6 * 3600 * 1000 * 1000 * 1000, "ns"), 6, None),
        (np.timedelta64(61, "s"), "61s", None),
        (np.timedelta64((2 * 3600 + 61) * 1000, "ms"), "7261s", None),
        (
            np.timedelta64((2 * 3600 + 61) * 1000 * 1000 * 1000, "ns"),
            "7261s",
            None,
        ),
    ],
)
def test_step_to_grib(step, expected_value, error):
    if error is None:
        assert step_to_grib(step) == expected_value
    else:
        with pytest.raises(error):
            step_to_grib(step)


@pytest.mark.parametrize(
    "d,expected_value,error",
    [
        (datetime.datetime(2002, 5, 2), (20020502, 0), None),
        (datetime.datetime(2002, 5, 2, 6), (20020502, 600), None),
        (datetime.datetime(2002, 5, 2, 12), (20020502, 1200), None),
        (np.int64(20020502), (20020502, 0), None),
        ("20020502", (20020502, 0), None),
        ("2002-05-02", (20020502, 0), None),
        ("2002-05-02T00", (20020502, 0), None),
        ("2002-05-02T00Z", (20020502, 0), None),
        ("2002-05-02T06", (20020502, 600), None),
        ("2002-05-02T06:11", (20020502, 611), None),
        ("2002-05-02T06:11:03", (20020502, 611), None),
        (datetime.datetime(2002, 5, 2, 6, 11, 3), (20020502, 611), None),
        (np.datetime64("2002-05-02"), (20020502, 0), None),
        (np.datetime64("2002-05-02T06"), (20020502, 600), None),
        (np.datetime64(0, "Y"), (19700101, 0), None),
    ],
)
def test_datetime_to_grib(d, expected_value, error):
    if error is None:
        assert datetime_to_grib(d) == expected_value
    else:
        with pytest.raises(error):
            datetime_to_grib(d)


@pytest.mark.parametrize(
    "step,expected_delta,error",
    [
        (12, datetime.timedelta(hours=12), None),
        ("12h", datetime.timedelta(hours=12), None),
        ("12s", datetime.timedelta(seconds=12), None),
        ("12m", datetime.timedelta(minutes=12), None),
        ("1m", datetime.timedelta(minutes=1), None),
        ("", None, (ValueError, TypeError)),
        ("m", None, (ValueError, TypeError, AttributeError)),
        ("1Z", None, (ValueError, TypeError)),
        ("m1", None, (ValueError, TypeError)),
        ("-1", None, (ValueError, TypeError)),
        ("-1s", None, (ValueError, TypeError)),
        ("1.1s", None, (ValueError, TypeError)),
    ],
)
def test_grib_step_to_timedelta(step, expected_delta, error):
    if error is None:
        assert grib_step_to_timedelta(step) == expected_delta
    else:
        with pytest.raises(error):
            grib_step_to_timedelta(step)


@pytest.mark.parametrize(
    "d,t,expected_value,error",
    [
        (20020502, 0, datetime.datetime(2002, 5, 2, 0), None),
        (20020502, 600, datetime.datetime(2002, 5, 2, 6), None),
        (20020502, 6, datetime.datetime(2002, 5, 2, 0, 6), None),
        (20020502, 630, datetime.datetime(2002, 5, 2, 6, 30), None),
        (20020502, 12, datetime.datetime(2002, 5, 2, 0, 12), None),
        (20020502, 1200, datetime.datetime(2002, 5, 2, 12), None),
        (1, 0, None, ValueError),
        (20020, 0, None, ValueError),
    ],
)
def test_grib_date_and_time_to_datetime(d, t, expected_value, error):
    if error is None:
        assert grib_date_and_time_to_datetime(d, t) == expected_value
    else:
        with pytest.raises(error):
            grib_date_and_time_to_datetime(d, t)
