from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from pathlib import Path
from shutil import copy2, copyfile, copytree, rmtree
from typing import TYPE_CHECKING

from ...colours import add_styles
from ..argparser import InlineArgumentParser
from ..command import Command
from .path_utils import backup, parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


def remove(path: Path) -> None | OSError:
    try:
        if path.is_dir():
            rmtree(path)
        else:
            path.unlink()
    except OSError as err:
        return OSError(f"Error: failed to remove {path.as_posix()!r}, {err}")


class Cp(Command):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "sources",
            type=str,
            nargs="+",
            help="source file(s) or directory(ies) path(s)",
        )
        self.parser.add_argument(
            "destination", type=str, help="destination directory path"
        )
        self.parser.add_argument(
            "-r",
            "--recursive",
            action="store_true",
            help="copy directories recursively",
        )
        self.parser.add_argument(
            "-p",
            "--preserve",
            action="store_true",
            help="preserve file and directory attributes",
        )
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="if the source exists at the destination, remove it, then copy the source",
        )
        self.parser.add_argument(
            "-n",
            "--no_clobber",
            action="store_true",
            help="do not overwrite an existing file(s) or directory(ies)",
        )
        self.parser.add_argument(
            "-i", "--interactive", action="store_true", help="prompt before overwrite"
        )
        self.parser.add_argument(
            "-b",
            "--backup",
            action="store_true",
            help="make a backup of each existing destination",
        )

    @classmethod
    def command(cls) -> str:
        return "cp"

    @staticmethod
    def description() -> str:
        return "Copy source to destination, or multiple source(s) to directory"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        destination = parse_path(options.destination, console.cwd)

        if not destination.is_absolute():
            destination = console.cwd / destination

        for source in map(partial(parse_path, cwd=console.cwd), options.sources):
            if not source.is_absolute():
                source = console.cwd / source

            if not source.exists():
                return FileNotFoundError(f"Error: {source.as_posix()!r} does not exist")

            # pathlib paths are immutable so here we make a copy
            dest_path = destination

            if dest_path.is_dir():
                if not options.recursive:
                    return IsADirectoryError(
                        f"Error: {dest_path.as_posix()!r} is a directory, "
                        "use -r to copy recursively"
                    )

                dest_path = dest_path / source.name

                if dest_path.is_relative_to(source):
                    return OSError(
                        f"Error: cannot cp {source.as_posix()!r} into "
                        f"itself {dest_path.as_posix()!r}"
                    )

            if dest_path.exists():
                if options.no_clobber:
                    continue

                if options.backup:
                    backup(dest_path, console.config.colours.errors)

                if options.force or (
                    options.interactive
                    and input(f"Overwrite: {dest_path.as_posix()!r}? [y/n]: ").lower()
                    == "y"
                ):
                    if (err := remove(dest_path)) is not None:
                        print(add_styles(str(err), console.config.colours.errors))
                else:
                    return FileExistsError(
                        f"Error: {dest_path.as_posix()!r} exists, "
                        "use -f to overwrite, or -b to backup"
                    )

            if options.preserve:
                copy_function = copy2
            else:
                copy_function = copyfile

            try:
                if source.is_dir():
                    copytree(source, dest_path, copy_function=copy_function)
                else:
                    copy_function(source, dest_path)
            except OSError as err:
                return OSError(f"Error: {err}")
