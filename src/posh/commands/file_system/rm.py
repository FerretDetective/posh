from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from os import walk
from pathlib import Path
from re import Pattern, error
from typing import TYPE_CHECKING, Callable

from ...colours import FgColour, add_colours
from ..argparser import InlineArgumentParser
from ..command import Executable
from ..regexp import compile_regexp
from .path_utils import check_ignore, parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


def remove_path(
    path: Path,
    force: bool,
    confirm_action: bool,
    ignore_checker: Callable[[Path], bool],
) -> None | Exception:
    if ignore_checker(path):
        return None

    is_file = path.is_file()

    # force overrides interactivity
    if not force and confirm_action:
        confirmation = input(
            f"Remove {'file' if is_file else 'directory'}: {path.as_posix()!r}? [y/n]: "
        )
        if confirmation.lower() != "y":
            return None

    try:
        if is_file:
            path.unlink()
        else:
            path.rmdir()

        return None
    except OSError as err:
        return OSError(f"Error: {err}")


def remove_recursively(
    path: Path, remover: Callable[[Path], None | Exception], err_style: FgColour
) -> None:
    for root, dirs, files in walk(path, topdown=False):
        root_path = Path(root)
        for name in dirs:
            if (err := remover(root_path / name)) is not None:
                print(add_colours(str(err), err_style))
        for name in files:
            if (err := remover(root_path / name)) is not None:
                print(add_colours(str(err), err_style))

    # walk doesn't include exclusively the root path
    if (err := remover(path)) is not None:
        print(add_colours(str(err), err_style))


def count_path_objs(path: Path) -> tuple[int, int]:
    files, dirs = 0, 1  # include current dir
    for _, dir_names, file_names in walk(path):
        files += len(file_names)
        dirs += len(dir_names)
    return (dirs, files)


class Rm(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "paths", type=str, nargs="+", help="path(s) to the object(s) to remove"
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="ignore nonexistent files, never prompt",
        )
        self.parser.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help="prompt before every removal",
        )
        self.parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="remove directories and their contents recursively",
        )
        self.parser.add_argument(
            "-d", "--dir", action="store_true", help="remove empty directories"
        )
        self.parser.add_argument(
            "-I",
            "--ignore_patterns",
            nargs="*",
            type=str,
            default=list[Pattern[str]](),
            help="ignore any path that matches the regular expression(s) note: uses fullmatching",
        )

    @classmethod
    def command(cls) -> str:
        return "rm"

    @staticmethod
    def description() -> str:
        return "Remove file(s) or directory(ies)"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        paths = list[Path]()
        for path in map(partial(parse_path, cwd=console.cwd), options.paths):
            if not path.is_absolute():
                path = console.cwd / path

            if not path.exists():
                if not options.force:
                    return FileNotFoundError(
                        f"Error: {path.as_posix()!r} does not exist"
                    )
                continue

            paths.append(path)

        # if the length of the paths is different that parsed.paths then atleast one of them is
        # invalid. however force overrides ignores invalid paths
        if len(paths) != len(options.paths) and not options.force:
            return None

        compiled_ignore_patterns = list[Pattern[str]]()
        for pattern in options.ignore_patterns:
            compiled = compile_regexp(pattern)
            if isinstance(compiled, error):
                return Exception(f"Error: {pattern!r} failied to compile, {compiled}")

            compiled_ignore_patterns.append(compiled)

        # if any patterns failed to compile return
        if len(compiled_ignore_patterns) != len(options.ignore_patterns):
            return None

        ignore = partial(
            check_ignore, ignores=[], ignore_patterns=compiled_ignore_patterns
        )
        remove = partial(
            remove_path,
            force=options.force,
            confirm_action=options.interactive,
            ignore_checker=ignore,
        )

        for path in paths:
            if path.is_dir():
                if options.recursive:
                    if options.force or options.interactive:
                        remove_recursively(path, remove, console.config.colours.errors)
                        continue

                    if sum((count := count_path_objs(path))) > 3:
                        confirmation = input(
                            f"Remove '{path.as_posix()},' and its "
                            f"{count[0]} subdirectories & {count[1]} files? [y/n]: "
                        )
                        if confirmation.lower() != "y":
                            continue

                    remove_recursively(path, remove, console.config.colours.errors)
                elif options.dir:
                    if ignore(path):
                        continue

                    if any(path.iterdir()):
                        return Exception(
                            f"Error: {path.as_posix()!r} is a non-empty directory. "
                            "Use -r, --recursive to remove it recursively."
                        )

                    try:
                        path.rmdir()
                    except OSError as err:
                        return OSError(f"Error: {err}")
                else:
                    return IsADirectoryError(
                        f"Error: {path.as_posix()!r} is a directory. "
                        "Use -d for empty directories or -r for to remove it recursively."
                    )
            else:
                return remove(path)

        return None
