from contextlib import nullcontext
from typing import Callable, List, Optional, TypeVar, Union

import pytest

from earthkit.dates.calendar import Weekday
from earthkit.dates.cli.cliargs import (
    Tuple,
    int_list,
    list_arg,
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
