from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Help(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "cmd",
            type=str,
            nargs="?",
            help=(
                "command to print the help page of, if none "
                "is provided list all availible commands"
            ),
        )

    @classmethod
    def command(cls) -> str:
        return "help"

    @staticmethod
    def description() -> str:
        return "Print the help page of a command"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        if not options.cmd:
            for cmd_string, command in sorted(
                console.commands.items(), key=lambda cmd: cmd[0]  # sort alphabetically
            ):
                print(f"{cmd_string:<9}: {command.description()}\n", end="")
        elif (command := console.commands.get(args[0])) is None:  # type: ignore
            return Exception(
                f"Error: unknown command {args[0]!r}",
            )
        else:
            print(command().help())

        return None
