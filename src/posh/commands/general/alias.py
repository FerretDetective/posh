from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .print_utils import print_dict

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Alias(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(
            self,
            epilog="To change an existing alias, first remove it then create a new alias",
        )
        self.parser.add_argument(
            "alias", nargs="?", help="alias for an existing command or alias"
        )
        self.parser.add_argument(
            "command", nargs="?", help="command for the alias to reference"
        )
        flag_group = self.parser.add_mutually_exclusive_group()
        flag_group.add_argument(
            "-p", "--print", action="store_true", help="print the current aliases"
        )
        flag_group.add_argument(
            "-s",
            "--save",
            required=False,
            action="store_true",
            help="saves the config to disk, equivalent to 'config -s'",
        )
        flag_group.add_argument("-r", "--remove", help="remove an existing alias")

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

        if options.print:
            print("Aliases:")
            print_dict(
                console.config.aliases,
                format_key=repr,
                format_val=lambda args: repr(" ".join(args)),
                seperator=" -> ",
                depth=1,
            )
        elif options.save:
            console.config.write_to_json()
        elif options.remove is not None:
            if options.remove not in console.config.aliases:
                return Exception(f"Error: alias {options.remove!r} does not exist")
            console.config.aliases.pop(options.remove)
        else:
            if not options.alias or not options.command:
                self.parser.print_usage()
                print(
                    "alias: error: the following arguments are required: alias, commands"
                )
                return

            console.config.aliases.update(
                console.config.parse_aliases({options.alias: options.command})
            )
            console.config.check_aliases()
