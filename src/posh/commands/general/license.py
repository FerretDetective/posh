from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ...colours import add_styles
from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class License(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_mutually_exclusive_group().add_argument(
            "-p", "--print", action="store_true", help="print the license"
        )
        self.parser.add_mutually_exclusive_group().add_argument(
            "-w",
            "--where",
            action="store_true",
            help="print the location of the product's license",
        )

    @classmethod
    def command(cls) -> str:
        return "license"

    @staticmethod
    def description() -> str:
        return "Print and locate this product's license"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        if all(not arg for arg in vars(options).values()):
            self.parser.print_usage()
            return

        if not console.data_directory.exists():
            return FileNotFoundError("Error: data directory is missing")

        if not (license_path := console.data_directory / "LICENSE.txt").exists():
            return FileNotFoundError("Error: couldn't find license file")

        if options.print:
            try:
                print(license_path.read_text())
            except OSError as err:
                return OSError(f"Error: couldn't read license, {err}")

        if options.where:
            path_str = license_path.as_posix()
            print(
                add_styles(
                    repr(path_str) if " " in path_str else path_str,
                    console.config.colours.file_path,
                )
            )
