from contextlib import nullcontext
from datetime import date
from typing import Tuple, Union

import pytest

from earthkit.time.calendar import (
    MonthInYear,
    Weekday,
    day_exists,
    month_length,
    parse_date,
    parse_mmdd,
    to_weekday,
)


@pytest.mark.parametrize(
    "arg, expected",
    [
        (-1, "^Week day out of range: "),
        (0, Weekday.MONDAY),
        (1, Weekday.TUESDAY),
        (7, "^Week day out of range: "),
        ("3", Weekday.THURSDAY),
        ("5", Weekday.SATURDAY),
        ("8", "^Week day out of range: "),
        ("M", Weekday.MONDAY),
        ("T", "^Ambiguous week day: "),
        ("wed", Weekday.WEDNESDAY),
        ("Fri", Weekday.FRIDAY),
        ("SUNDAY", Weekday.SUNDAY),
        ("Notaday", "^Unrecognised week day: "),
    ],
)
def test_to_weekday(arg: Union[int, str], expected: Union[Weekday, str]):
    context = nullcontext()
    if isinstance(expected, str):
        context = pytest.raises(ValueError, match=expected)
    with context:
        assert to_weekday(arg) == expected


@pytest.mark.parametrize(
    "year, month, expected",
    [
        (2000, 1, 31),
        (2001, 2, 28),
        (2002, 3, 31),
        (2003, 4, 30),
        (2004, 5, 31),
        (2005, 6, 30),
        (2006, 7, 31),
        (2007, 8, 31),
        (2008, 9, 30),
        (2009, 10, 31),
        (2010, 11, 30),
        (2011, 12, 31),
        (2012, 2, 29),
        (2013, 13, "^Invalid month: 13$"),
    ],
)
def test_month_length(year: int, month: int, expected: Union[int, str]):
    context = nullcontext()
    if isinstance(expected, str):
        context = pytest.raises(ValueError, match=expected)
    with context:
        assert month_length(year, month) == expected


@pytest.mark.parametrize(
    "year, month, day, expected",
    [
        (1999, 0, 12, False),
        (2000, 1, 32, False),
        (2001, 2, 29, False),
        (2002, 13, 18, False),
        (2003, 8, -5, False),
        (2004, 2, 29, True),
        (2005, 6, 31, False),
        (2006, 7, 31, True),
    ],
)
def test_day_exists(year: int, month: int, day: int, expected: bool):
    assert day_exists(year, month, day) == expected


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
    "year, month, day, expected",
    [
        (2010, 1, 3, True),
        (2011, 2, 29, False),
        (2012, 2, 29, True),
        (2013, 3, date(2012, 3, 1), False),
        (2014, 4, date(2014, 3, 8), False),
        (2015, 5, date(2015, 5, 28), True),
        (2016, 6, 31, False),
        (2017, 7, 32, False),
        (2018, 8, 0, False),
    ],
)
def test_monthinyear_contains(
    year: int, month: int, day: Union[int, date], expected: bool
):
    ymonth = MonthInYear(year, month)
    assert (day in ymonth) == expected


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


@pytest.mark.parametrize(
    "arg, expected",
    [
        ((5,), "^not enough values to unpack"),
        ((10, 3), (10, 3)),
        ((4, 31), "^Invalid day: "),
        ("14", "^Unrecognised month-day value: "),
        ("test", "^Unrecognised month-day value: "),
        ("1304", "^Invalid month: "),
        ("0230", "^Invalid day: "),
        ("0906", (9, 6)),
        ("1213", (12, 13)),
    ],
)
def test_parse_mmdd(
    arg: Union[Tuple[int, int], str], expected: Union[Tuple[int, int], str]
):
    context = nullcontext()
    if isinstance(expected, str):
        context = pytest.raises(ValueError, match=expected)
    with context:
        assert parse_mmdd(arg) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
        pytest.param("", None, id="empty"),
        pytest.param("2020", None, id="yearonly"),
        pytest.param("202005", None, id="yearmonthonly"),
        pytest.param("20202503", None, id="notadate"),
        pytest.param("20201204", (2020, 12, 4), id="ok"),
        pytest.param("202010251200", None, id="toolong"),
        pytest.param((2022,), "^not enough values to unpack", id="tup-inclomplete"),
        pytest.param((2022, 2, 3), (2022, 2, 3), id="tup-ok"),
        pytest.param((2022, 2, 30), "^Invalid date: ", id="tup-ok"),
    ],
)
def test_parse_date(arg: str, expected: Union[Tuple[int, int, int], None]):
    context = nullcontext()
    if expected is None:
        context = pytest.raises(ValueError, match="^Unrecognised date format: ")
    elif isinstance(expected, str):
        context = pytest.raises(ValueError, match=expected)
    else:
        expected = date(*expected)
    with context:
        assert parse_date(arg) == expected
