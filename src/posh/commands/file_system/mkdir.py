from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .path_utils import parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Mkdir(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "paths", nargs="+", type=str, help="path(s) to the directory(ies)"
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="write over pre-existing directories",
        )
        self.parser.add_argument(
            "-p",
            "--parents",
            action="store_true",
            help="make parent directories as needed",
        )

    @classmethod
    def command(cls) -> str:
        return "mkdir"

    @staticmethod
    def description() -> str:
        return "Create empty directory(ies) from path(s)"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        for path in map(partial(parse_path, cwd=console.cwd), options.paths):
            if not path.is_absolute():
                path = console.cwd / path

            if options.parents:
                try:
                    path.mkdir(parents=True)
                except OSError as err:
                    return OSError(f"Error: {err}")
            else:
                if path.exists() and not options.force:
                    return FileExistsError(
                        f"Error: {path.as_posix()!r} already exists, "
                        "use -f, --force to overwrite it."
                    )
                try:
                    path.mkdir(exist_ok=True)
                except OSError as err:
                    return OSError(f"Error: {err}")

        return None
