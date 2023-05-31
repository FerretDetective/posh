from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Clear(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)

    @classmethod
    def command(cls) -> str:
        return "clear"

    @staticmethod
    def description() -> str:
        return "Clear console's output"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if self.parser.parse_arguments(args) is None:
            return

        print("\033c", end="")
