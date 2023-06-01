from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from ..argparser import InlineArgumentParser
from ..command import Executable
from .path_utils import parse_path

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Cat(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument(
            "paths", type=str, nargs="+", help="path(s) to the file(s)"
        )
        self.parser.add_argument(
            "-n", "--number", action="store_true", help="show line numbers"
        )
        self.parser.add_argument(
            "-e",
            "--show_ends",
            action="store_true",
            help="display $ at end of each line",
        )
        self.parser.add_argument(
            "-t",
            "--show_tabs",
            action="store_true",
            help="display TAB characters as ^I",
        )
        self.parser.add_argument(
            "-s",
            "--squeeze_blank",
            action="store_true",
            help="suppress repeated empty output lines",
        )
        self.parser.add_argument(
            "-v",
            "--show_nonprinting",
            action="store_true",
            help="use ^ and M- notation, except for LFD and TAB",
        )
        self.parser.add_argument(
            "-b",
            "--number_nonblank",
            action="store_true",
            help="number non-empty output lines, overrides -n",
        )

    @classmethod
    def command(cls) -> str:
        return "cat"

    @staticmethod
    def description() -> str:
        return "Concatenate the contents of a file and print them to the console"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        paths = list[Path]()
        for path_string in options.paths:
            path = parse_path(path_string, console.cwd)

            if not path.is_absolute():
                path = console.cwd / path

            if not path.exists():
                return FileNotFoundError(f"Error: {path_string!r} does not exist")

            if not path.is_file():
                return OSError(f"Error: {path.as_posix()!r} is an invalid file.")

            paths.append(path)

        line_number = 1  # maintains count between multiple files
        for path in paths:
            try:
                with open(path, "rb") as file:
                    previous_line_blank = False

                    for line in file:
                        try:
                            line = line.decode("utf8")
                        except UnicodeDecodeError as err:
                            return Exception(
                                f"Error: failed to decode line {line}, {err}"
                            )

                        # suppress multiple blank lines
                        if options.squeeze_blank and line.rstrip("\n") == "":
                            if previous_line_blank:
                                continue
                            previous_line_blank = True
                        else:
                            previous_line_blank = False

                        if options.show_tabs:
                            line = line.replace("\t", "^I")

                        if options.show_nonprinting:
                            printable_line = ""
                            for index, char in enumerate(line):
                                if char == "\t":
                                    printable_line += "^I"
                                elif char == "\r":
                                    printable_line += "^M"
                                elif char == "\n":
                                    # if the LF is the last char its considered a normal char
                                    if index == len(line) - 1:
                                        printable_line += "\n"
                                    else:
                                        printable_line += "^J\n"
                                # if not ascii presentable use the unicode number
                                elif (o := ord(char)) < 32 or o > 126:
                                    printable_line += f"^{o:03}"  # 3 zero padded
                                else:
                                    printable_line += char
                            line = printable_line

                        # only number lines if -b and the line isn't blank or -n & not -b
                        # since -b overrides -n
                        if (options.number_nonblank and line.rstrip("\n") != "") or (
                            options.number and not options.number_nonblank
                        ):
                            line = f"{line_number:>6}  {line}"
                            line_number += 1

                        # show ends if -e & there is a trailing LF
                        if options.show_ends and line.rstrip("\n") != line:
                            line = line.rstrip("\n") + "$\n"

                        print(line.rstrip("\n"))
            except OSError as err:
                return OSError(f"Error: {err}")
