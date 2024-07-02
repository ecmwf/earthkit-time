from datetime import date
from typing import List, Optional, Tuple

import pytest

from earthkit.time.cli.cliout import format_date, format_date_list


@pytest.mark.parametrize(
    "ymd, expected", [((1999, 11, 22), "19991122"), ((2000, 1, 3), "20000103")]
)
def test_format_date(ymd: Tuple[int, int, int], expected: str):
    assert format_date(date(*ymd)) == expected


@pytest.mark.parametrize(
    "dates, sep, expected",
    [
        (
            [(2000, 1, 1), (2000, 1, 2), (2000, 1, 3)],
            None,
            "20000101/20000102/20000103",
        ),
        ([(2010, 5, 3)], None, "20100503"),
        ([], None, ""),
        (
            [(y, 12, 12) for y in range(2005, 2010)],
            ":",
            "20051212:20061212:20071212:20081212:20091212",
        ),
        ([(2002, 1, 5), (2002, 2, 5)], "\n", "20020105\n20020205"),
        ([(1999, 5, 8), (2003, 2, 4)], ", ", "19990508, 20030204"),
    ],
)
def test_format_date_list(
    dates: List[Tuple[int, int, int]], sep: Optional[str], expected: str
):
    if sep is None:
        assert format_date_list([date(*ymd) for ymd in dates]) == expected
    else:
        assert format_date_list([date(*ymd) for ymd in dates], sep=sep) == expected
