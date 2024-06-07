from contextlib import nullcontext

import pytest

from earthkit.dates.calendar import MonthInYear


@pytest.mark.parametrize(
    "year, month, ok", [(y, y - 2009, y > 2009 and y < 2022) for y in range(2005, 2025)]
)
def test_monthinyear_create(year: int, month: int, ok: bool):
    context = (
        nullcontext() if ok else pytest.raises(ValueError, match="^Invalid month:")
    )
    with context:
        ymonth = MonthInYear(year, month)
    if ok:
        assert ymonth.year == year
        assert ymonth.month == month


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (1993, 1, 31),
        (1994, 2, 28),
        (1996, 2, 29),
        (1995, 3, 31),
        (1997, 4, 30),
        (1998, 5, 31),
        (1999, 6, 30),
        (2000, 7, 31),
        (2001, 8, 31),
        (2002, 9, 30),
        (2003, 10, 31),
        (2004, 11, 30),
        (2005, 12, 31),
    ],
)
def test_monthinyear_length(year: int, month: int, expected: int):
    ymonth = MonthInYear(year, month)
    assert ymonth.length() == expected


@pytest.mark.parametrize(
    "year, month, eyear, emonth",
    [(1954, 3, 1954, 4), (2020, 12, 2021, 1), (2005, 1, 2005, 2), (1976, 11, 1976, 12)],
)
def test_monthinyear_next(year: int, month: int, eyear: int, emonth: int):
    ymonth = MonthInYear(year, month)
    next_ymonth = ymonth.next()
    assert next_ymonth.year == eyear
    assert next_ymonth.month == emonth


@pytest.mark.parametrize(
    "year, month, eyear, emonth",
    [(2050, 6, 2050, 5), (1972, 1, 1971, 12), (1999, 2, 1999, 1), (2013, 12, 2013, 11)],
)
def test_monthinyear_previous(year: int, month: int, eyear: int, emonth: int):
    ymonth = MonthInYear(year, month)
    prev_ymonth = ymonth.previous()
    assert prev_ymonth.year == eyear
    assert prev_ymonth.month == emonth
