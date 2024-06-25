import argparse
from datetime import timedelta
from typing import List, Optional

from ..calendar import parse_date
from .actions import ActionParser
from .cliout import format_date


def date_shift_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    delta = timedelta(days=args.days)
    print(format_date(args.date + delta))


def date_diff_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    delta = args.date1 - args.date2
    print(delta.days)


def get_parser() -> argparse.ArgumentParser:
    parser = ActionParser(description="Date manipulation tools")

    shift_action = parser.add_action(
        "shift",
        date_shift_action,
        help="shift a date",
        description="Shift a date by the given number of days",
    )
    shift_action.add_argument("date", type=parse_date, help="reference date")
    shift_action.add_argument("days", type=int, help="number of days (can be negative)")

    diff_action = parser.add_action(
        "diff",
        date_diff_action,
        help="subtract two dates",
        description="Subtract DATE2 from DATE1, returning the number of days",
    )
    diff_action.add_argument("date1", type=parse_date, help="first date (+)")
    diff_action.add_argument("date2", type=parse_date, help="second date (-)")

    return parser


def main(sys_args: Optional[List[str]] = None):
    parser = get_parser()
    args = parser.parse_args(sys_args)
    if args.action is None:
        parser.error("Please specify an action")
    args.action(parser, args)


if __name__ == "__main__":
    main()
