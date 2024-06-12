import argparse
import textwrap
from datetime import date, datetime
from typing import Iterable, List, Optional, Tuple

from ..calendar import Weekday, day_exists, month_length
from ..climatology import date_range, model_climate_dates
from ..sequence import DailySequence, MonthlySequence, WeeklySequence, YearlySequence


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


def format_date(d: date) -> str:
    return d.strftime("%Y%m%d")


def format_date_list(dates: Iterable[date]) -> str:
    return "/".join(format_date(d) for d in dates)


def weekday_arg(arg: str) -> Weekday:
    if arg.isdigit():
        arg = int(arg)
        if arg not in range(7):
            raise ValueError(f"Week day out of range: {arg} not in 0-6")
        return Weekday(arg)
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


def date_range_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    dates = date_range(args.date, args.start, args.end)
    print(format_date_list(dates))


def model_climate_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    reference = args.date
    start = args.start
    end = args.end
    before = args.before
    after = args.after
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
    dates = model_climate_dates(reference, start, end, before, after, seq)
    print(format_date_list(dates))


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Tools to compute model climate dates", fromfile_prefix_chars="@"
    )
    parser.set_defaults(action=None)
    actions = parser.add_subparsers(
        title="actions",
        metavar="<action>",
        help="use `%(prog)s %(metavar)s --help` for details",
    )

    range_action = actions.add_parser(
        "range",
        help="compute climatological date ranges",
        description="Compute climatological date ranges, one day per year in a given range",
    )
    range_action.set_defaults(action=date_range_action)
    range_action.add_argument("date", type=date_arg, help="reference date")

    range_start_group = range_action.add_mutually_exclusive_group(required=True)
    range_start_group.add_argument(
        "--from-date", type=date_arg, dest="start", help="starting date"
    )
    range_start_group.add_argument(
        "--from-year", type=int, dest="start", help="starting year"
    )

    range_end_group = range_action.add_mutually_exclusive_group(required=True)
    range_end_group.add_argument(
        "--to-date", type=date_arg, dest="end", help="ending date"
    )
    range_end_group.add_argument("--to-year", type=int, dest="end", help="ending year")

    mclim_action = actions.add_parser(
        "mclim",
        help="compute sets of dates for model climatologies",
        description="""Compute sets of dates for model climatologies

        This combines a climatological range (same day in multiple years) and a
        recurring source (e.g. twice a week).
        """,
        epilog=textwrap.dedent(
            """
            WEEKDAYS: week days can be specified either by number (0 = Monday, 1 =
            Tuesday, etc) or by any unambiguous prefix of the name
            (case-insensitive, e.g. M, tue, Friday)

            EXCLUDES: specific days can be excluded from sequences:
            * daily: exclude specific days of the month
            * monthly: exclude specific dates in the year (MMDD)
            * yearly: exclude specific dates (YYYYMMDD)
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mclim_action.set_defaults(action=model_climate_action)
    mclim_action.add_argument("date", type=date_arg, help="reference date")

    mclim_start_group = mclim_action.add_mutually_exclusive_group(required=True)
    mclim_start_group.add_argument(
        "--from-date", type=date_arg, dest="start", help="starting date"
    )
    mclim_start_group.add_argument(
        "--from-year", type=int, dest="start", help="starting year"
    )

    mclim_end_group = mclim_action.add_mutually_exclusive_group(required=True)
    mclim_end_group.add_argument(
        "--to-date", type=date_arg, dest="end", help="ending date"
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

    mclim_seq_group = mclim_action.add_mutually_exclusive_group(required=True)
    mclim_seq_group.add_argument("--daily", action="store_true", help="daily inputs")
    mclim_seq_group.add_argument(
        "--weekly",
        type=weekly_days,
        default=None,
        help="weekly inputs on these days (see WEEKDAYS, slash-separated)",
    )
    mclim_seq_group.add_argument(
        "--monthly",
        type=int_list,
        default=None,
        help="monthly inputs on these days (slash-separated)",
    )
    mclim_seq_group.add_argument(
        "--yearly",
        type=yearly_days,
        default=None,
        help="yearly inputs on these days (MMDD, slash-separated)",
    )

    mclim_action.add_argument(
        "--exclude",
        type=list_arg,
        default=[],
        help="exclude these dates (see EXCLUDES, slash-separated)",
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
