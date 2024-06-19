from datetime import date, timedelta

import pytest

from earthkit.time import date_range, model_climate_dates
from earthkit.time.calendar import MONDAY, THURSDAY
from earthkit.time.sequence import MonthlySequence, WeeklySequence


def test_date_range_leapyear():
    # reference is leap
    assert list(date_range(date(2020, 2, 29), 2018, 2020)) == [
        date(2018, 2, 28),
        date(2019, 2, 28),
        date(2020, 2, 28),
    ]

    # reference is leap (2)
    assert list(date_range(date(2020, 2, 29), date(2017, 2, 28), date(2019, 3, 1))) == [
        date(2017, 2, 28),
        date(2018, 2, 28),
        date(2019, 2, 28),
    ]

    # start is leap (1)
    assert list(date_range(date(2022, 3, 1), date(2020, 2, 29), date(2023, 3, 1))) == [
        date(2020, 3, 1),
        date(2021, 3, 1),
        date(2022, 3, 1),
        date(2023, 3, 1),
    ]

    # start is leap (2)
    assert list(date_range(date(2022, 2, 28), date(2020, 2, 29), date(2023, 3, 1))) == [
        date(2021, 2, 28),
        date(2022, 2, 28),
        date(2023, 2, 28),
    ]

    # end is leap (1)
    assert list(date_range(date(2022, 3, 1), date(2020, 2, 28), date(2024, 2, 29))) == [
        date(2020, 3, 1),
        date(2021, 3, 1),
        date(2022, 3, 1),
        date(2023, 3, 1),
    ]

    # end is leap (2)
    assert list(
        date_range(date(2022, 2, 28), date(2020, 2, 28), date(2024, 2, 29))
    ) == [
        date(2020, 2, 28),
        date(2021, 2, 28),
        date(2022, 2, 28),
        date(2023, 2, 28),
        date(2024, 2, 28),
    ]

    # start and end are leap (1)
    assert list(date_range(date(2022, 3, 1), date(2020, 2, 29), date(2024, 2, 29))) == [
        date(2020, 3, 1),
        date(2021, 3, 1),
        date(2022, 3, 1),
        date(2023, 3, 1),
    ]

    # start and end are leap (2)
    assert list(
        date_range(date(2022, 2, 28), date(2020, 2, 29), date(2024, 2, 29))
    ) == [
        date(2021, 2, 28),
        date(2022, 2, 28),
        date(2023, 2, 28),
        date(2024, 2, 28),
    ]

    # reference and start are leap
    assert list(date_range(date(2020, 2, 29), date(2016, 2, 29), date(2019, 3, 1))) == [
        date(2017, 2, 28),
        date(2018, 2, 28),
        date(2019, 2, 28),
    ]

    # reference and end are leap
    assert list(
        date_range(date(2020, 2, 29), date(2017, 2, 28), date(2020, 2, 29))
    ) == [
        date(2017, 2, 28),
        date(2018, 2, 28),
        date(2019, 2, 28),
        date(2020, 2, 28),
    ]

    # all dates are leap
    assert list(
        date_range(date(2020, 2, 29), date(2016, 2, 29), date(2020, 2, 29))
    ) == [
        date(2017, 2, 28),
        date(2018, 2, 28),
        date(2019, 2, 28),
        date(2020, 2, 28),
    ]

    with pytest.raises(ValueError, match="^Unknown recurrence"):
        list(date_range(date(2021, 1, 2), 2000, 2004, "sesquiannually"))


def test_model_climate_dates():
    assert list(
        model_climate_dates(
            date(2024, 2, 29),
            2020,
            2023,
            timedelta(days=7),
            timedelta(days=7),
            WeeklySequence([MONDAY, THURSDAY]),
        )
    ) == [
        date(y, m, d)
        for y in range(2020, 2024)
        for m, d in [(2, 22), (2, 26), (2, 28), (3, 4), (3, 7)]
    ]

    assert list(
        model_climate_dates(
            date(2024, 3, 2),
            date(2020, 1, 1),
            date(2024, 1, 1),
            timedelta(days=10),
            timedelta(days=10),
            MonthlySequence(range(1, 32, 4), excludes=[(2, 29)]),
        )
    ) == [
        date(y, m, d)
        for y in range(2020, 2024)
        for m, d in [(2, 21), (2, 25), (3, 1), (3, 5), (3, 9)]
    ]
