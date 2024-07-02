import argparse
from typing import List, Optional

from ..calendar import parse_date
from ..climatology import date_range, model_climate_dates
from .actions import ActionParser
from .cliargs import (
    SEP_EPILOG,
    SEQ_EPILOG,
    add_sep_arg,
    add_sequence_args,
    create_sequence,
)
from .cliout import format_date_list


def date_range_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    dates = date_range(args.date, args.start, args.end)
    print(format_date_list(dates, sep=args.sep))


def model_climate_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    reference = args.date
    start = args.start
    end = args.end
    before = args.before
    after = args.after
    seq = create_sequence(parser, args)
    dates = model_climate_dates(reference, start, end, before, after, seq)
    print(format_date_list(dates, sep=args.sep))


def get_parser() -> argparse.ArgumentParser:
    parser = ActionParser(
        description="Tools to compute model climate dates", fromfile_prefix_chars="@"
    )

    range_action = parser.add_action(
        "range",
        date_range_action,
        help="compute climatological date ranges",
        description="Compute climatological date ranges, one day per year in a given range",
        epilog=SEP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    range_action.add_argument("date", type=parse_date, help="reference date")

    range_start_group = range_action.add_mutually_exclusive_group(required=True)
    range_start_group.add_argument(
        "--from-date", type=parse_date, dest="start", help="starting date"
    )
    range_start_group.add_argument(
        "--from-year", type=int, dest="start", help="starting year"
    )

    range_end_group = range_action.add_mutually_exclusive_group(required=True)
    range_end_group.add_argument(
        "--to-date", type=parse_date, dest="end", help="ending date"
    )
    range_end_group.add_argument("--to-year", type=int, dest="end", help="ending year")

    add_sep_arg(range_action)

    mclim_action = parser.add_action(
        "mclim",
        model_climate_action,
        help="compute sets of dates for model climatologies",
        description="""Compute sets of dates for model climatologies

        This combines a climatological range (same day in multiple years) and a
        recurring source (e.g. twice a week).
        """,
        epilog=SEQ_EPILOG + "\n" + SEP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mclim_action.add_argument("date", type=parse_date, help="reference date")

    mclim_start_group = mclim_action.add_mutually_exclusive_group(required=True)
    mclim_start_group.add_argument(
        "--from-date", type=parse_date, dest="start", help="starting date"
    )
    mclim_start_group.add_argument(
        "--from-year", type=int, dest="start", help="starting year"
    )

    mclim_end_group = mclim_action.add_mutually_exclusive_group(required=True)
    mclim_end_group.add_argument(
        "--to-date", type=parse_date, dest="end", help="ending date"
    )
    mclim_end_group.add_argument("--to-year", type=int, dest="end", help="ending year")

    mclim_action.add_argument(
        "--before",
        required=True,
        metavar="NUM",
        type=int,
        help="pick up all inputs starting from %(metavar)s days before the chosen date",
    )
    mclim_action.add_argument(
        "--after",
        required=True,
        metavar="NUM",
        type=int,
        help="pick up all inputs up to %(metavar)s days after the chosen date",
    )

    add_sequence_args(mclim_action)
    add_sep_arg(mclim_action)

    return parser


def main(sys_args: Optional[List[str]] = None):
    parser = get_parser()
    args = parser.parse_args(sys_args)
    if args.action is None:
        parser.error("Please specify an action")
    args.action(parser, args)


if __name__ == "__main__":
    main()
