import argparse
from typing import List, Tuple

from ..calendar import Weekday, parse_date, parse_mmdd, to_weekday
from ..sequence import (
    DailySequence,
    MonthlySequence,
    Sequence,
    WeeklySequence,
    YearlySequence,
)


def weekly_days(arg: str) -> List[Weekday]:
    if not arg:
        return []
    return [to_weekday(elem) for elem in arg.split("/")]


def int_list(arg: str) -> List[int]:
    if not arg:
        return []
    return [int(elem) for elem in arg.split("/")]


def yearly_days(arg: str) -> List[Tuple[int, int]]:
    if not arg:
        return []
    return [parse_mmdd(elem) for elem in arg.split("/")]


def list_arg(arg: str) -> List[str]:
    if not arg:
        return []
    return arg.split("/")


SEQ_EPILOG = """
WEEKDAYS: week days can be specified either by number (0 = Monday, 1 = Tuesday,
etc) or by any unambiguous prefix of the name (case-insensitive, e.g. M, tue,
Friday)

PRESETS: sequence presets can be stored in the package as well as externally
defined. If a preset name is given, the corresponding file will be searched in
``EARTHKIT_TIME_SEQ_PATH``, then in the package itself

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
    seq_group.add_argument(
        "--preset",
        default=None,
        help="name of a preset sequence, or path to a valid YAML preset file (see PRESETS)",
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
            excludes = [parse_mmdd(elem) for elem in args.exclude]
            seq = MonthlySequence(args.monthly, excludes=excludes)
        elif args.yearly is not None:
            excludes = [parse_date(elem) for elem in args.exclude]
            seq = YearlySequence(args.yearly, excludes=excludes)
        elif args.preset is not None:
            seq = Sequence.from_resource(args.preset)
    except ValueError as e:
        parser.error(str(e))
    assert seq is not None, "Unsupported sequence?!"
    return seq
