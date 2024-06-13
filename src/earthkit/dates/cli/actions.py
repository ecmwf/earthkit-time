import argparse
from typing import Callable


class ActionParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_defaults(action=None)
        self.action_subparsers = self.add_subparsers(
            title="actions",
            metavar="<action>",
            help="use `%(prog)s %(metavar)s --help` for details",
            parser_class=argparse.ArgumentParser,  # otherwise we add actions recursively
        )

    def add_action(
        self,
        name: str,
        func: Callable[[argparse.ArgumentParser, argparse.Namespace], None],
        **kwargs,
    ) -> argparse.ArgumentParser:
        action = self.action_subparsers.add_parser(name, **kwargs)
        action.set_defaults(action=func)
        return action
