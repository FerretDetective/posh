from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ...colours import add_styles
from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Pwd(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)

    @classmethod
    def command(cls) -> str:
        return "pwd"

    @staticmethod
    def description() -> str:
        return "Print the current working directory"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if self.parser.parse_arguments(args) is None:
            return

        print(
            add_styles(
                f"{string!r}" if " " in (string := console.cwd.as_posix()) else string,
                console.config.colours.directory_path,
            )
        )
