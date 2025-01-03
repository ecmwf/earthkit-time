import argparse
from datetime import date

import pytest

from earthkit.time.calendar import Weekday
from earthkit.time.cli.sequence import (
    seq_bracket_action,
    seq_nearest_action,
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
        pytest.param(
            {"monthly": [5, 20], "skip": 2, "date": date(2007, 4, 3)},
            "20070505",
            id="skip",
        ),
        pytest.param(
            {"monthly": [5, 20], "skip": 2, "date": date(2007, 4, 5)},
            "20070520",
            id="skip-exc",
        ),
        pytest.param(
            {
                "monthly": [5, 20],
                "skip": 2,
                "inclusive": True,
                "date": date(2007, 4, 5),
            },
            "20070505",
            id="skip-inc",
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
    args.setdefault("skip", 0)
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
        pytest.param(
            {"monthly": [5, 20], "skip": 2, "date": date(2007, 4, 10)},
            "20070305",
            id="skip",
        ),
        pytest.param(
            {"monthly": [5, 20], "skip": 2, "date": date(2007, 4, 5)},
            "20070220",
            id="skip-exc",
        ),
        pytest.param(
            {
                "monthly": [5, 20],
                "skip": 2,
                "inclusive": True,
                "date": date(2007, 4, 5),
            },
            "20070305",
            id="skip-inc",
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
    args.setdefault("skip", 0)
    args = argparse.Namespace(**args)
    seq_prev_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "date": date(2006, 7, 26)}, "20060726", id="daily"
        ),
        pytest.param(
            {"daily": True, "date": date(2017, 3, 30), "exclude": ["30", "31"]},
            "20170329",
            id="daily-excludes",
        ),
        pytest.param(
            {
                "weekly": [Weekday.TUESDAY, Weekday.THURSDAY, Weekday.SATURDAY],
                "date": date(2013, 10, 23),
                "resolve": "previous",
            },
            "20131022",
            id="weekly",
        ),
        pytest.param(
            {"monthly": [1, 15], "date": date(1995, 8, 25)},
            "19950901",
            id="monthly",
        ),
        pytest.param(
            {
                "yearly": [(1, 4), (12, 25)],
                "date": date(2009, 12, 30),
                "resolve": "next",
            },
            "20100104",
            id="yearly",
        ),
    ],
)
def test_seq_nearest(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args.setdefault("daily", False)
    args.setdefault("weekly", None)
    args.setdefault("monthly", None)
    args.setdefault("yearly", None)
    args.setdefault("exclude", [])
    args.setdefault("resolve", "previous")
    args = argparse.Namespace(**args)
    seq_nearest_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "from": date(2008, 3, 12), "to": date(2008, 3, 20)},
            "\n".join(f"200803{d:02d}" for d in range(12, 21)),
            id="daily",
        ),
        pytest.param(
            {
                "weekly": [Weekday.SUNDAY],
                "from": date(2010, 9, 5),
                "to": date(2010, 10, 17),
                "exclude_start": True,
            },
            "\n".join(
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
            "\n".join(
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
            "\n".join(
                f"{y:04d}{m:02d}{d:02d}" for y, m, d in [(2014, 1, 15), (2014, 7, 20)]
            ),
            id="yearly-nostart-noend",
        ),
        pytest.param(
            {
                "daily": True,
                "from": date(2016, 11, 2),
                "to": date(2016, 11, 6),
                "sep": " ",
            },
            " ".join(
                f"{y:04d}{m:02d}{d:02d}"
                for y, m, d in [
                    (2016, 11, 2),
                    (2016, 11, 3),
                    (2016, 11, 4),
                    (2016, 11, 5),
                    (2016, 11, 6),
                ]
            ),
            id="daily-sep",
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
    args.setdefault("sep", "\n")
    args = argparse.Namespace(**args)
    seq_range_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        pytest.param(
            {"daily": True, "date": date(2015, 3, 26)}, "20150325\n20150327", id="daily"
        ),
        pytest.param(
            {
                "weekly": [Weekday.WEDNESDAY, Weekday.SATURDAY],
                "date": date(2016, 10, 4),
                "before": 2,
            },
            "\n".join(
                f"2016{m:02d}{d:02d}" for m, d in [(9, 28), (10, 1), (10, 5), (10, 8)]
            ),
            id="weekly-2",
        ),
        pytest.param(
            {"monthly": [14], "date": date(2017, 7, 14), "before": 2, "after": 1},
            "\n".join(f"2017{m:02d}14" for m in [5, 6, 8]),
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
            "\n".join(
                f"{y:04d}{m:02d}{d:02d}"
                for y, m, d in [(2019, 2, 2), (2019, 3, 3), (2019, 4, 4), (2020, 1, 1)]
            ),
            id="yearly-1-2-inc",
        ),
        pytest.param(
            {"daily": True, "date": date(2020, 8, 29), "sep": ", "},
            "20200828, 20200830",
            id="daily-sep",
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
    args.setdefault("sep", "\n")
    args = argparse.Namespace(**args)
    seq_bracket_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
