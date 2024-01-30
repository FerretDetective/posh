from __future__ import annotations

from collections.abc import Sequence
from sys import exit as sys_exit
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Exit(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "exit_code",
            nargs="?",
            type=int,
            default=0,
            help="code to exit with, default is 0",
        )

    @classmethod
    def command(cls) -> str:
        return "exit"

    @staticmethod
    def description() -> str:
        return "Exit the program with the given exit code"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        sys_exit(options.exit_code)
