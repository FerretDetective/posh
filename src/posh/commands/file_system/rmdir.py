from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .path_utils import parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Rmdir(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument("paths", type=str, nargs="+", help="")
        self.parser.add_argument(
            "-p",
            "--parents",
            action="store_true",
            help="remove  directory  and its ancestors; e.g., 'rmdir "
            "-p a/b/c' is similar to 'rmdir a/b/c a/b a'",
        )

    @classmethod
    def command(cls) -> str:
        return "rmdir"

    @staticmethod
    def description() -> str:
        return "Remove directory(ies), if they are empty"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        for name, path in zip(
            options.paths, map(partial(parse_path, cwd=console.cwd), options.paths)
        ):
            if not path.is_absolute():
                path = console.cwd / path

            if options.parents:
                root = parse_path(name, console.cwd)

                # iterate while the relative path is equal to the absolute path
                # removing the the current directory
                while path.name == root.name:
                    if not path.exists():
                        return FileNotFoundError(
                            f"Error: {path.as_posix()!r} does not exist"
                        )

                    if any(path.iterdir()):
                        return FileExistsError(
                            f"Error: {path.as_posix()!r} is not empty."
                        )

                    try:
                        path.rmdir()
                    except OSError as err:
                        return OSError(f"Error: {err}")
                    path = path.parent
                    root = root.parent
            else:
                if not path.is_dir():
                    if not path.exists():
                        return FileExistsError(
                            f"Error: {path.as_posix()!r} does not exist."
                        )
                    return OSError(f"Error: {path.as_posix()!r} is not a directory.")

                if any(path.iterdir()):
                    return FileExistsError(f"Error: {path.as_posix()!r} is not empty.")

                try:
                    path.rmdir()
                except OSError as err:
                    return OSError(f"Error: {err}")

        return None
