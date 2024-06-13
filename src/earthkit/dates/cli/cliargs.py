import argparse
from datetime import date, datetime
from typing import List, Tuple

from earthkit.dates.sequence import (
    DailySequence,
    MonthlySequence,
    Sequence,
    WeeklySequence,
    YearlySequence,
)

from ..calendar import Weekday, day_exists, month_length


def date_arg(arg: str) -> date:
    try_formats = ["%Y%m%d"]
    dt = None
    for fmt in try_formats:
        try:
            dt = datetime.strptime(arg, fmt)
        except ValueError:
            continue
        else:
            break
    if dt is None:
        raise ValueError(f"Unrecognised date format: {arg!r}")
    return dt.date()


def weekday_arg(arg: str) -> Weekday:
    if arg.isdigit():
        iarg = int(arg)
        if iarg not in range(7):
            raise ValueError(f"Week day out of range: {arg} not in 0-6")
        return Weekday(iarg)
    arg = arg.upper()
    matching = [wd for wd in Weekday if wd.name.startswith(arg)]
    if not matching:
        raise ValueError(f"Unrecognised week day: {arg!r}")
    if len(matching) > 1:
        others = ", ".join(wd.name.capitalize() for wd in matching)
        raise ValueError(f"Ambiguous week day: {arg!r} could be any of {others}")
    return matching[0]


def weekly_days(arg: str) -> List[Weekday]:
    if not arg:
        return []
    return [weekday_arg(elem) for elem in arg.split("/")]


def int_list(arg: str) -> List[int]:
    if not arg:
        return []
    return [int(elem) for elem in arg.split("/")]


def mmdd_arg(arg: str) -> Tuple[int, int]:
    if len(arg) != 4:
        raise ValueError(f"Unrecognised month-day value: {arg!r}")
    mm = arg[:2]
    dd = arg[2:]
    if not mm.isdigit() or not dd.isdigit():
        raise ValueError(f"Unrecognised month-day value: {arg!r}")
    m = int(mm)
    if m not in range(1, 13):
        raise ValueError(f"Invalid month: {m} not in 1-12")
    d = int(dd)
    if not day_exists(2000, m, d):
        raise ValueError(f"Invalid day: {d} not in 1-{month_length(2000, m)}")
    return (m, d)


def yearly_days(arg: str) -> List[Tuple[int, int]]:
    if not arg:
        return []
    return [mmdd_arg(elem) for elem in arg.split("/")]


def list_arg(arg: str) -> List[str]:
    if not arg:
        return []
    return arg.split("/")


SEQ_EPILOG = """
WEEKDAYS: week days can be specified either by number (0 = Monday, 1 = Tuesday,
etc) or by any unambiguous prefix of the name (case-insensitive, e.g. M, tue,
Friday)

EXCLUDES: specific days can be excluded from sequences:
* daily: exclude specific days of the month
* monthly: exclude specific dates in the year (MMDD)
* yearly: exclude specific dates (YYYYMMDD)
"""


def add_sequence_args(parser: argparse.ArgumentParser):
    seq_group = parser.add_mutually_exclusive_group(required=True)
    seq_group.add_argument("--daily", action="store_true", help="daily inputs")
    seq_group.add_argument(
        "--weekly",
        type=weekly_days,
        default=None,
        help="weekly inputs on these days (see WEEKDAYS, slash-separated)",
    )
    seq_group.add_argument(
        "--monthly",
        type=int_list,
        default=None,
        help="monthly inputs on these days (slash-separated)",
    )
    seq_group.add_argument(
        "--yearly",
        type=yearly_days,
        default=None,
        help="yearly inputs on these days (MMDD, slash-separated)",
    )

    parser.add_argument(
        "--exclude",
        type=list_arg,
        default=[],
        help="exclude these dates (see EXCLUDES, slash-separated)",
    )


def create_sequence(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> Sequence:
    seq = None
    try:
        if args.daily:
            try:
                excludes = [int(elem) for elem in args.exclude]
            except ValueError as e:
                raise ValueError(
                    "Invalid excludes, must be a slash-separated list of days"
                ) from e
            seq = DailySequence(excludes=excludes)
        elif args.weekly is not None:
            seq = WeeklySequence(args.weekly)
        elif args.monthly is not None:
            excludes = [mmdd_arg(elem) for elem in args.exclude]
            seq = MonthlySequence(args.monthly, excludes=excludes)
        elif args.yearly is not None:
            excludes = [date_arg(elem) for elem in args.exclude]
            seq = YearlySequence(args.yearly, excludes=excludes)
    except ValueError as e:
        parser.error(str(e))
    assert seq is not None, "Unsupported sequence?!"
    return seq
