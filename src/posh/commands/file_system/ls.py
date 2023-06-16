from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from os import listdir, walk
from os.path import getsize
from pathlib import Path
from re import Pattern, error
from typing import TYPE_CHECKING

from natsort import natsorted

from ...colours import TextStyle, add_styles
from ..argparser import InlineArgumentParser
from ..command import Executable
from ..regexp import compile_regexp
from .path_utils import check_ignore, is_hidden, parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


def is_int(n: float) -> bool:
    return n % 1 == 0


def get_readable_size(size: float, ndigits: int = 2) -> str:
    prefixes = ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi")
    for prefix in prefixes:
        if size < 1024:
            return f"{int(size) if is_int(size) else round(size, ndigits)}{prefix}B"

        size /= 1024

    return f"{round(size, ndigits)}{prefixes[-1]}B"


def get_format_string(
    path: Path,
    show_all: bool,
    show_type: bool,
    show_size: bool,
    human_readable: bool,
    ignore: list[str],
    ignore_patterns: list[Pattern[str]],
    directory_style: TextStyle,
    file_style: TextStyle,
) -> str:
    if check_ignore(path, ignore, ignore_patterns) or (
        is_hidden(path) and not show_all
    ):
        return ""

    output = ""
    if show_type:
        if path.is_file():
            output += add_styles("f  ", file_style)
        else:
            output += add_styles("d  ", directory_style)

    if human_readable:  # overrides show_size
        output += f"{get_readable_size(getsize(path)):<10}  "
    elif show_size:
        output += f"{getsize(path):<10}  "

    output += add_styles(
        repr(path.name) if " " in path.name else path.name,
        file_style if path.is_file() else directory_style,
    )

    return output + "\n"


class Ls(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "path", type=str, nargs="?", default=".", help="path to the directory"
        )
        self.parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="include hidden files & directories",
        )
        self.parser.add_argument(
            "-t",
            "--show_type",
            action="store_true",
            help="show whether an object is a file or directory",
        )
        self.parser.add_argument(
            "-s",
            "--show_size",
            action="store_true",
            help="show the size of the file in bytes",
        )
        self.parser.add_argument(
            "-R",
            "--human_readable",
            action="store_true",
            help="show the size in a human readable fashion",
        )
        self.parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="list subdirectories recursively",
        )
        self.parser.add_argument(
            "-i",
            "--ignore",
            nargs="*",
            type=str,
            default=list[str](),
            help="ignore anything equal the given string(s)",
        )
        self.parser.add_argument(
            "-I",
            "--ignore_patterns",
            nargs="*",
            type=str,
            default=list[Pattern[str]](),
            help="ignore any path that matches the regular expression",
        )

    @classmethod
    def command(cls) -> str:
        return "ls"

    @staticmethod
    def description() -> str:
        return "Print the contents of a given directory"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        parsed_string_path = parse_path(options.path, console.cwd)
        path = parsed_string_path

        if not path.is_absolute():
            path = console.cwd / path

        if not path.exists():
            return FileNotFoundError(f"Error: {options.path!r} does not exist.")

        compiled_ignore_patterns = list[Pattern[str]]()
        for pattern in options.ignore_patterns:
            compiled = compile_regexp(pattern)
            if isinstance(compiled, error):
                return Exception(f"Error: {pattern!r} failied to compile, {compiled}")
            compiled_ignore_patterns.append(compiled)

        format_path = partial(
            get_format_string,
            show_all=options.all,
            show_type=options.show_type,
            show_size=options.show_size,
            human_readable=options.human_readable,
            ignore=options.ignore,
            ignore_patterns=compiled_ignore_patterns,
            directory_style=console.config.colours.directory_path,
            file_style=console.config.colours.file_path,
        )

        if options.recursive:
            # this preserves the relative path when printing
            # exg: ~/foo/bar => ./food/bar
            if path == console.cwd and options.path == ".":
                relative_root = "."
            else:
                relative_root = parsed_string_path.as_posix()

            hidden_exclude = None
            for root, dir_names, file_names in walk(path):
                root_path = Path(root)
                if not options.all:
                    if is_hidden(root_path):
                        # if hidden hasn't be used yet or the root isn't a child of the
                        # hidden_exclude, set the hidden exlcude to the root
                        if hidden_exclude is None or not root_path.is_relative_to(
                            hidden_exclude
                        ):
                            hidden_exclude = root_path
                        continue
                    # anything that is a child of a hidden directory should also be hidden
                    if hidden_exclude is not None and root_path.is_relative_to(
                        hidden_exclude
                    ):
                        continue

                # never ignore the starting path, otherwise check whether to ignore
                if root_path != path and check_ignore(
                    root_path, options.ignore, compiled_ignore_patterns
                ):
                    continue

                # the relative root is either the path to the directory of a "." and since
                # Path(".").parts == (), it will handle relative as well as aboslute paths
                path_string = relative_root + "".join(
                    f"/{part}" for part in root_path.relative_to(path).parts
                )
                print(f"{repr(path_string) if ' ' in path_string else path_string}:")

                for dir_name in dir_names:
                    print(format_path(Path(root, dir_name)), end="")

                for file_name in file_names:
                    print(format_path(Path(root, file_name)), end="")

                print()
        else:
            for file in natsorted(listdir(path)):
                print(format_path(path / file), end="")
