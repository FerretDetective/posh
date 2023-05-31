from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Command
from .print_utils import print_dict

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Alias(Command):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        create_alias_group = self.parser.add_argument_group()
        create_alias_group.add_argument(
            "alias", nargs="?", help="alias for an existing command or alias"
        )
        create_alias_group.add_argument(
            "command", nargs="?", help="command for the alias to reference"
        )
        self.parser.add_argument_group().add_argument(
            "-p", "--print", action="store_true", help="print the current aliases"
        )

    @classmethod
    def command(cls) -> str:
        return "alias"

    @staticmethod
    def description() -> str:
        return "Create an alias for a string of commands"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return
        # TODO: remove the ability to create an alias with a spacec in the key
        if options.print:
            print("Aliases:")
            print_dict(
                console.config.aliases, format_func=repr, seperator=" -> ", depth=1
            )
        else:
            if not options.alias or not options.command:
                self.parser.print_usage()
                print(
                    "alias: error: the following arguments are required: alias, commands"
                )
                return

            console.config.aliases[options.alias] = options.command
