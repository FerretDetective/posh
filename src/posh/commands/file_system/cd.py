from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .path_utils import parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Cd(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument("path", type=str, help="path to the directory")

    @classmethod
    def command(cls) -> str:
        return "cd"

    @staticmethod
    def description() -> str:
        return "Change the current working directory"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | OSError:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        path = parse_path(options.path, console.cwd)

        if not path.is_absolute():
            path = console.cwd / path

        if not path.exists():
            return FileNotFoundError(f"Error: {path.as_posix()!r} does not exist.")

        if path.is_file():
            return NotADirectoryError(f"Error: {path.as_posix()!r} is a file.")

        console.cwd = path

        return None
