import argparse
from datetime import date

import pytest

from earthkit.time.calendar import Weekday
from earthkit.time.cli.sequence import (
    seq_bracket_action,
    seq_next_action,
    seq_prev_action,
    seq_range_action,
)


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "date": date(1999, 12, 31)}, "20000101", id="daily"
        ),
        pytest.param(
            {"daily": True, "date": date(1999, 12, 31), "inclusive": True},
            "19991231",
            id="daily-inc",
        ),
        pytest.param(
            {"weekly": [Weekday.FRIDAY, Weekday.SUNDAY], "date": date(2000, 5, 17)},
            "20000519",
            id="weekly",
        ),
        pytest.param(
            {
                "yearly": [(2, 28), (2, 29)],
                "exclude": ["20040228"],
                "date": date(2003, 2, 28),
            },
            "20040229",
            id="yearly-excludes",
        ),
        pytest.param(
            {
                "yearly": [(2, 28), (2, 29)],
                "exclude": ["20040228"],
                "date": date(2003, 2, 28),
                "inclusive": True,
            },
            "20030228",
            id="yearly-excludes-inc",
        ),
    ],
)
def test_seq_next(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args.setdefault("inclusive", False)
    args = argparse.Namespace(**args)
    seq_next_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {
                "weekly": [Weekday.TUESDAY, Weekday.THURSDAY, Weekday.SATURDAY],
                "date": date(2005, 4, 30),
            },
            "20050428",
            id="weekly",
        ),
        pytest.param(
            {
                "weekly": [Weekday.TUESDAY, Weekday.THURSDAY, Weekday.SATURDAY],
                "date": date(2005, 4, 30),
                "inclusive": True,
            },
            "20050430",
            id="weekly-inc",
        ),
        pytest.param(
            {"monthly": [1, 15], "date": date(2006, 10, 23), "inclusive": True},
            "20061015",
            id="monthly",
        ),
    ],
)
def test_seq_prev(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args.setdefault("inclusive", False)
    args = argparse.Namespace(**args)
    seq_prev_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "from": date(2008, 3, 12), "to": date(2008, 3, 20)},
            "/".join(f"200803{d:02d}" for d in range(12, 21)),
            id="daily",
        ),
        pytest.param(
            {
                "weekly": [Weekday.SUNDAY],
                "from": date(2010, 9, 5),
                "to": date(2010, 10, 17),
                "exclude_start": True,
            },
            "/".join(
                f"2010{m:02d}{d:02d}"
                for m, d in [(9, 12), (9, 19), (9, 26), (10, 3), (10, 10), (10, 17)]
            ),
            id="weekly-nostart",
        ),
        pytest.param(
            {
                "monthly": [10, 12],
                "from": date(2012, 7, 10),
                "to": date(2012, 10, 12),
                "exclude_end": True,
            },
            "/".join(
                f"2012{m:02d}{d:02d}"
                for m, d in [
                    (7, 10),
                    (7, 12),
                    (8, 10),
                    (8, 12),
                    (9, 10),
                    (9, 12),
                    (10, 10),
                ]
            ),
            id="monthly-noend",
        ),
        pytest.param(
            {
                "yearly": [(1, 15), (7, 20)],
                "from": date(2013, 7, 20),
                "to": date(2015, 1, 15),
                "exclude_start": True,
                "exclude_end": True,
            },
            "/".join(
                f"{y:04d}{m:02d}{d:02d}" for y, m, d in [(2014, 1, 15), (2014, 7, 20)]
            ),
            id="yearly-nostart-noend",
        ),
    ],
)
def test_seq_range(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args.setdefault("exclude_start", False)
    args.setdefault("exclude_end", False)
    args = argparse.Namespace(**args)
    seq_range_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "date": date(2015, 3, 26)}, "20150325/20150327", id="daily"
        ),
        pytest.param(
            {
                "weekly": [Weekday.WEDNESDAY, Weekday.SATURDAY],
                "date": date(2016, 10, 4),
                "before": 2,
            },
            "/".join(
                f"2016{m:02d}{d:02d}" for m, d in [(9, 28), (10, 1), (10, 5), (10, 8)]
            ),
            id="weekly-2",
        ),
        pytest.param(
            {"monthly": [14], "date": date(2017, 7, 14), "before": 2, "after": 1},
            "/".join(f"2017{m:02d}14" for m in [5, 6, 8]),
            id="monthly-2-1",
        ),
        pytest.param(
            {
                "yearly": [(1, 1), (2, 2), (3, 3), (4, 4)],
                "date": date(2019, 3, 3),
                "before": 1,
                "after": 2,
                "inclusive": True,
            },
            "/".join(
                f"{y:04d}{m:02d}{d:02d}"
                for y, m, d in [(2019, 2, 2), (2019, 3, 3), (2019, 4, 4), (2020, 1, 1)]
            ),
            id="yearly-1-2-inc",
        ),
    ],
)
def test_seq_bracket(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args.setdefault("before", 1)
    args.setdefault("after", None)
    args.setdefault("inclusive", False)
    args = argparse.Namespace(**args)
    seq_bracket_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
