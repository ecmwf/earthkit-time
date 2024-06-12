import argparse
from contextlib import nullcontext
from datetime import date
from typing import Callable, List, Optional, Tuple, TypeVar, Union

import pytest

from earthkit.dates.calendar import Weekday
from earthkit.dates.cli.climatology import (
    date_arg,
    date_range_action,
    format_date,
    format_date_list,
    int_list,
    list_arg,
    mmdd_arg,
    model_climate_action,
    weekday_arg,
    weekly_days,
    yearly_days,
)

T = TypeVar("T")
U = TypeVar("U")


def parsing_test(
    arg: str,
    expected: Union[T, str, None],
    parsing_func: Callable[[str], U],
    convert_expected: Optional[Callable[[T], U]] = None,
    default_error: Optional[str] = None,
):
    context = nullcontext()
    if expected is None:
        context = pytest.raises(ValueError, match=default_error)
    elif isinstance(expected, str):
        context = pytest.raises(ValueError, match=expected)
    elif convert_expected is not None:
        expected = convert_expected(expected)
    with context:
        assert parsing_func(arg) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
        pytest.param("", None, id="empty"),
        pytest.param("2020", None, id="yearonly"),
        pytest.param("202005", None, id="yearmonthonly"),
        pytest.param("20202503", None, id="notadate"),
        pytest.param("20201204", (2020, 12, 4), id="ok"),
        pytest.param("202010251200", None, id="toolong"),
    ],
)
def test_date_arg(arg: str, expected: Union[Tuple[int, int, int], None]):
    parsing_test(
        arg, expected, date_arg, (lambda exp: date(*exp)), "^Unrecognised date format: "
    )


@pytest.mark.parametrize(
    "ymd, expected", [((1999, 11, 22), "19991122"), ((2000, 1, 3), "20000103")]
)
def test_format_date(ymd: Tuple[int, int, int], expected: str):
    assert format_date(date(*ymd)) == expected


@pytest.mark.parametrize(
    "dates, expected",
    [
        ([(2000, 1, 1), (2000, 1, 2), (2000, 1, 3)], "20000101/20000102/20000103"),
        ([(2010, 5, 3)], "20100503"),
        ([], ""),
    ],
)
def test_format_date_list(dates: List[Tuple[int, int, int]], expected: str):
    assert format_date_list([date(*ymd) for ymd in dates]) == expected


@pytest.mark.parametrize(
    "arg, expected",
    [
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
def test_weekday_arg(arg: str, expected: Union[Weekday, str]):
    parsing_test(arg, expected, weekday_arg)


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("", []),
        ("1", [Weekday.TUESDAY]),
        ("Mon/Thu", [Weekday.MONDAY, Weekday.THURSDAY]),
        ("123/456", "^Week day out of range: "),
    ],
)
def test_weekly_days(arg: str, expected: Union[List[Weekday], str]):
    parsing_test(arg, expected, weekly_days)


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("", []),
        ("22", [22]),
        ("1/3/5", [1, 3, 5]),
        ("foo", "^invalid literal for int"),
        ("2/3/foo", "^invalid literal for int"),
    ],
)
def test_int_list(arg: str, expected: Union[List[int], str]):
    parsing_test(arg, expected, int_list)


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("14", "^Unrecognised month-day value: "),
        ("test", "^Unrecognised month-day value: "),
        ("1304", "^Invalid month: "),
        ("0230", "^Invalid day: "),
        ("0906", (9, 6)),
        ("1213", (12, 13)),
    ],
)
def test_mmdd_arg(arg: str, expected: Union[Tuple[int, int], str]):
    parsing_test(arg, expected, mmdd_arg)


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("", []),
        ("1211", [(12, 11)]),
        ("0119/0219/0319", [(1, 19), (2, 19), (3, 19)]),
        ("0403/date/1012", "^Unrecognised month-day value: "),
        ("0129/0230/0331", "^Invalid day: "),
    ],
)
def test_yearly_days(arg: str, expected: Union[List[Tuple[int, int]], str]):
    parsing_test(arg, expected, yearly_days)


@pytest.mark.parametrize(
    "arg, expected",
    [
        ("", []),
        ("foo", ["foo"]),
        ("foo/bar", ["foo", "bar"]),
        ("1/2/3/spam", ["1", "2", "3", "spam"]),
    ],
)
def test_list_arg(arg: str, expected: List[str]):
    parsing_test(arg, expected, list_arg)


@pytest.mark.parametrize(
    "ref, start, end, expected",
    [
        (
            date(2024, 3, 5),
            2000,
            2005,
            "20000305/20010305/20020305/20030305/20040305/20050305",
        ),
        (
            date(2024, 12, 1),
            date(2010, 1, 1),
            date(2016, 1, 1),
            "20101201/20111201/20121201/20131201/20141201/20151201",
        ),
    ],
)
def test_date_range_action(
    ref: date,
    start: Union[date, int],
    end: Union[date, int],
    expected: str,
    capsys: pytest.CaptureFixture[str],
):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(date=ref, start=start, end=end)
    date_range_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {
                "date": date(2024, 5, 22),
                "start": 2020,
                "end": 2023,
                "before": 7,
                "after": 7,
                "weekly": [Weekday.MONDAY, Weekday.THURSDAY],
            },
            "/".join(
                f"{y}{m:02d}{d:02d}"
                for y in range(2020, 2024)
                for m, d in [(5, 16), (5, 20), (5, 23), (5, 27)]
            ),
            id="weekly",
        ),
        pytest.param(
            {
                "date": date(2024, 7, 3),
                "start": date(2015, 8, 1),
                "end": date(2017, 8, 1),
                "before": 10,
                "after": 9,
                "monthly": [1, 5, 9, 13, 17, 21, 25, 29],
            },
            "/".join(
                f"{y}{m:02d}{d:02d}"
                for y in range(2016, 2018)
                for m, d in [(6, 25), (6, 29), (7, 1), (7, 5), (7, 9)]
            ),
            id="monthly",
        ),
        pytest.param(
            {
                "date": date(2024, 3, 2),
                "start": 2012,
                "end": date(2015, 1, 1),
                "before": 6,
                "after": 3,
                "monthly": [1, 5, 9, 13, 17, 21, 25, 29],
                "exclude": ["0229"],
            },
            "/".join(
                f"{y}{m:02d}{d:02d}"
                for y in range(2012, 2015)
                for m, d in [(2, 25), (3, 1), (3, 5)]
            ),
            id="monthly-exclude",
        ),
    ],
)
def test_model_climate_action(
    args: dict, expected: str, capsys: pytest.CaptureFixture[str]
):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args = argparse.Namespace(**args)
    model_climate_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
