import argparse
from datetime import date
from typing import Union

import pytest

from earthkit.dates.calendar import Weekday
from earthkit.dates.cli.climatology import date_range_action, model_climate_action


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
