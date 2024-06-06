from datetime import date

from earthkit.dates import date_range


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
