from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from shutil import move
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .path_utils import backup, parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Mv(Executable):
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
            "-f",
            "--force",
            action="store_true",
            help="overwrite if the destination already exists",
        )
        self.parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            help="move source(s) only if they are newer than the "
            "existing file(s) at the destination",
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
        return "mv"

    @staticmethod
    def description() -> str:
        return "Rename source to destination, or move source(s) to directory"

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

            dest_path = destination

            # if the destination is a directory we move the source into that directory
            if dest_path.is_dir():
                dest_path = dest_path / source.name

                # check if attempting to move the source into itself
                if dest_path.is_relative_to(source):
                    return OSError(
                        f"Error: cannot move {source.as_posix()!r} into "
                        f"itself {dest_path.as_posix()!r}"
                    )

            if dest_path.exists():
                if options.no_clobber:
                    continue

                if options.interactive:
                    if (
                        input(f"Overwrite: {dest_path.as_posix()!r}? [y/n]: ").lower()
                        != "y"
                    ):
                        continue

                if (
                    options.update
                    and source.stat().st_mtime <= dest_path.stat().st_mtime
                ):
                    continue

                if options.backup:
                    backup(dest_path, console.config.colours.errors)
                elif (
                    not options.force and not options.update and not options.interactive
                ):
                    return FileExistsError(
                        f"Error: {dest_path.as_posix()!r} exists, "
                        "use -f to overwrite, -u to update, or -b to backup",
                    )

            try:
                move(source, dest_path)
            except OSError as err:
                return OSError(f"Error: {err}")
