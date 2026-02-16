import argparse
from datetime import timedelta
from typing import List, Optional

from ..calendar import parse_datetime
from .actions import ActionParser
from .cliout import format_datetime


def datetime_shift_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    delta = timedelta(hours=args.hours)
    print(format_datetime(args.datetime + delta))


def datetime_diff_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    delta = args.datetime1 - args.datetime2
    print(round(delta.total_seconds() / 3600))


def get_parser() -> argparse.ArgumentParser:
    parser = ActionParser(description="Datetime manipulation tools")

    shift_action = parser.add_action(
        "shift",
        datetime_shift_action,
        help="shift a datetime",
        description="Shift a datetime by the given number of hours",
    )
    shift_action.add_argument(
        "datetime", type=parse_datetime, help="reference datetime"
    )
    shift_action.add_argument(
        "hours", type=int, help="number of hours (can be negative)"
    )

    diff_action = parser.add_action(
        "diff",
        datetime_diff_action,
        help="subtract two datetimes",
        description="Subtract DATETIME2 from DATETIME1, returning the number of hours",
    )
    diff_action.add_argument(
        "datetime1", type=parse_datetime, help="first datetime (+)"
    )
    diff_action.add_argument(
        "datetime2", type=parse_datetime, help="second datetime (-)"
    )

    return parser


def main(sys_args: Optional[List[str]] = None):
    parser = get_parser()
    args = parser.parse_args(sys_args)
    if args.action is None:
        parser.error("Please specify an action")
    args.action(parser, args)


if __name__ == "__main__":
    main()
