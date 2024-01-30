from dataclasses import dataclass, field
from pathlib import Path

from ..colours import add_colours
from .interpreter import Interpreter


@dataclass
class Traceback:
    err: BaseException
    file: Path | None = field(default=None)
    line: str | None = field(default=None)
    line_no: int | None = field(default=None)
    whitespace: str = field(default="  ")

    def format_traceback(self) -> str:
        file_string = (
            repr(self.file.as_posix()) if self.file is not None else "unknown file"
        )
        line_string = self.line if self.line is not None else "uknown line"
        line_no_string = (
            str(self.line_no) if self.line_no is not None else "unknown line number"
        )
        return (
            "Traceback (most recent call last):\n"
            f"{self.whitespace}File: {file_string}, line {line_no_string}:\n"
            f"{self.whitespace * 2}{line_string}\n"
            f"{self.whitespace * 2}{'^'*len(line_string)}\n"
            f"{self.whitespace}{self.err}"
        )


class FileIntepreter(Interpreter):
    def __init__(self, starting_directory: Path, file: Path) -> None:
        super().__init__(starting_directory)
        self.config.record_history = False
        self.file_path = file

    def main(self) -> None:
        try:
            with open(self.file_path, "rb") as file:
                for index, line_bytes in enumerate(file, start=1):
                    try:
                        line = line_bytes.decode("utf8").strip()
                    except UnicodeDecodeError as err:
                        print(
                            add_colours(
                                f"Error: parsing failed on line {index} in file "
                                f"{self.file_path.as_posix()!r}, {err}"
                            )
                        )
                        return
                    try:
                        error: BaseException | None = self.interpret_command(line)
                    except KeyboardInterrupt:
                        error = KeyboardInterrupt("Error: KEYBOARD INTERRUPT")

                    if error is not None:
                        print(
                            add_colours(
                                Traceback(
                                    error, self.file_path, line, index
                                ).format_traceback(),
                                self.config.colours.errors,
                            )
                        )
                        return
        except OSError as err:
            print(
                add_colours(
                    f"Error: failed to open file {self.file_path.as_posix()!r}, {err}",
                    self.config.colours.errors,
                )
            )
        except KeyboardInterrupt:
            print(add_colours("Error: KEYBOARD INTERUPT", self.config.colours.errors))
