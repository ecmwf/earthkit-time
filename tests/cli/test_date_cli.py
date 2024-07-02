import argparse
from datetime import date

import pytest

from earthkit.time.cli.date import date_diff_action, date_shift_action


@pytest.mark.parametrize(
    "args, expected",
    [
        ({"date": date(1996, 5, 30), "days": 25}, "19960624"),
        ({"date": date(1998, 3, 17), "days": -18}, "19980227"),
        ({"date": date(2018, 7, 12), "days": 0}, "20180712"),
        ({"date": date(2023, 11, 2), "days": 366}, "20241102"),
        ({"date": date(2003, 12, 24), "days": -365}, "20021224"),
    ],
)
def test_date_shift(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(**args)
    date_shift_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"


@pytest.mark.parametrize(
    "args, expected",
    [
        ({"date1": date(2022, 8, 27), "date2": date(2022, 8, 14)}, "13"),
        ({"date1": date(2001, 1, 28), "date2": date(2001, 2, 26)}, "-29"),
        ({"date1": date(2014, 3, 26), "date2": date(2014, 3, 26)}, "0"),
        ({"date1": date(2006, 2, 17), "date2": date(1995, 6, 22)}, "3893"),
        ({"date1": date(2008, 1, 7), "date2": date(2019, 1, 5)}, "-4016"),
    ],
)
def test_date_diff(args: dict, expected: str, capsys: pytest.CaptureFixture[str]):
    parser = argparse.ArgumentParser()
    args = argparse.Namespace(**args)
    date_diff_action(parser, args)
    captured = capsys.readouterr()
    assert captured.out == expected + "\n"
