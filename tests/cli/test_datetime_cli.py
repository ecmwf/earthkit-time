import argparse
from datetime import datetime

import pytest

from earthkit.time.cli.datetime import datetime_diff_action, datetime_shift_action


@pytest.mark.parametrize(
    "args, expected",
    [
        ({"datetime": datetime(1997, 8, 31, 18), "hours": 12}, "1997090106"),
        ({"datetime": datetime(1995, 3, 5, 6), "hours": -240}, "1995022306"),
        ({"datetime": datetime(2015, 2, 10, 0), "hours": 0}, "2015021000"),
        ({"datetime": datetime(2023, 11, 2, 12), "hours": 366 * 24}, "2024110212"),
        ({"datetime": datetime(2003, 12, 24, 0), "hours": -365 * 24}, "2002122400"),
    ],
)
def test_datetime_shift(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(**args)
    datetime_shift_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        (
            {
                "datetime1": datetime(2025, 3, 12, 18),
                "datetime2": datetime(2025, 3, 12, 5),
            },
            "13",
        ),
        (
            {
                "datetime1": datetime(2022, 8, 27, 6),
                "datetime2": datetime(2022, 8, 14, 12),
            },
            "306",
        ),
        (
            {
                "datetime1": datetime(2001, 1, 28, 6),
                "datetime2": datetime(2001, 2, 26, 18),
            },
            "-708",
        ),
        (
            {
                "datetime1": datetime(2014, 3, 26, 0),
                "datetime2": datetime(2014, 3, 26, 0),
            },
            "0",
        ),
        (
            {
                "datetime1": datetime(2006, 2, 17, 21),
                "datetime2": datetime(2004, 6, 22, 15),
            },
            "14526",
        ),
        (
            {
                "datetime1": datetime(2008, 1, 7, 0),
                "datetime2": datetime(2009, 1, 5, 16),
            },
            "-8752",
        ),
    ],
)
def test_datetime_diff(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(**args)
    datetime_diff_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
