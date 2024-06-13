from datetime import date
from typing import List, Tuple

import pytest

from earthkit.dates.cli.cliout import format_date, format_date_list


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
