from __future__ import annotations

from collections.abc import Sequence
from subprocess import run
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Run(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self, add_help=False)
        self.parser.add_argument("cmd", type=str, help="command to run")

    @classmethod
    def command(cls) -> str:
        return "run"

    @staticmethod
    def description() -> str:
        return "Start a process with any given arguments"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if (options := self.parser.parse_known_arguments(args)) is None:
            return

        run(
            " ".join(
                (f'"{arg}"' if " " in arg else arg)
                for arg in (options[0].cmd, *options[1])
            ),
            shell=True,
            check=False,
            cwd=console.cwd,
        )
