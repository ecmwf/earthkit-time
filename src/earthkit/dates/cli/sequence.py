import argparse
from typing import List, Optional

from ..calendar import parse_date
from .actions import ActionParser
from .cliargs import SEQ_EPILOG, add_sequence_args, create_sequence
from .cliout import format_date, format_date_list


def seq_next_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    seq = create_sequence(parser, args)
    print(format_date(seq.next(args.date, strict=(not args.inclusive))))


def seq_prev_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    seq = create_sequence(parser, args)
    print(format_date(seq.previous(args.date, strict=(not args.inclusive))))


def seq_range_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    seq = create_sequence(parser, args)
    print(
        format_date_list(
            seq.range(
                getattr(args, "from"),
                args.to,
                (not args.exclude_start),
                (not args.exclude_end),
            )
        )
    )


def seq_bracket_action(parser: argparse.ArgumentParser, args: argparse.Namespace):
    num = args.before
    if args.after is not None:
        num = (args.before, args.after)
    seq = create_sequence(parser, args)
    print(format_date_list(seq.bracket(args.date, num, strict=(not args.inclusive))))


def get_parser() -> argparse.ArgumentParser:
    parser = ActionParser(
        description="Manipulate sequences of dates", fromfile_prefix_chars="@"
    )

    next_action = parser.add_action(
        "next",
        seq_next_action,
        help="compute the next date in the given sequence",
        description="Compute the next date in the given sequence",
        epilog=SEQ_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    next_action.add_argument("date", type=parse_date, help="reference date")
    add_sequence_args(next_action)
    next_action.add_argument(
        "--inclusive",
        action="store_true",
        help="if the given date is in the sequence, return it",
    )

    prev_action = parser.add_action(
        "previous",
        seq_prev_action,
        help="compute the previous date in the given sequence",
        description="Compute the previous date in the given sequence",
        epilog=SEQ_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    prev_action.add_argument("date", type=parse_date, help="reference date")
    add_sequence_args(prev_action)
    prev_action.add_argument(
        "--inclusive",
        action="store_true",
        help="if the given date is in the sequence, return it",
    )

    range_action = parser.add_action(
        "range",
        seq_range_action,
        help="compute the sequence dates that fall within a range",
        description="Compute the sequence dates that fall winthin the given range",
        epilog=SEQ_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_sequence_args(range_action)
    range_action.add_argument("from", type=parse_date, help="starting date")
    range_action.add_argument("to", type=parse_date, help="ending date")
    range_action.add_argument(
        "--exclude-start", action="store_true", help="exclude starting date"
    )
    range_action.add_argument(
        "--exclude-end", action="store_true", help="exclude ending date"
    )

    bracket_action = parser.add_action(
        "bracket",
        seq_bracket_action,
        help="compute the sequence dates around a date",
        description="Compute the sequence dates around the given date",
        epilog=SEQ_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_sequence_args(bracket_action)
    bracket_action.add_argument("date", type=parse_date, help="reference date")
    bracket_action.add_argument(
        "before",
        nargs="?",
        type=int,
        default=1,
        help="number of dates before the given date (default 1)",
    )
    bracket_action.add_argument(
        "after",
        nargs="?",
        type=int,
        default=None,
        help="number of dates after the given date (default: same as before)",
    )
    bracket_action.add_argument(
        "--inclusive",
        action="store_true",
        help="include the given date in the sequence",
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
