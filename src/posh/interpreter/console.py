from __future__ import annotations

from functools import cache
from getpass import getuser
from os import get_terminal_size
from pathlib import Path
from time import strftime

from ..colours import BasicStyle, add_styles
from .interpreter import Interpreter


@cache
def shorten_path(path: Path, length: int, root_str: str) -> str:
    # makes sure at least the topmost directory is showing
    parts = [path.name]
    path = path.parent

    while len(f"{root_str}{'/'.join(parts)}/{path.name}") < length:
        parts.append(path.name)
        path = path.parent

    return f"{root_str}{Path(*reversed(parts)).as_posix()}"


def right_pad(string: str, length: int, char: str = " ") -> str:
    return (length - len(string)) * char + string


class Console(Interpreter):
    def input_string(self) -> str:
        output = ""

        if self.config.show_time:
            output += add_styles(
                right_pad(f"[{strftime('%X')}] ", get_terminal_size().columns) + "\r",
                self.config.colours.time,
                BasicStyle.BOLD,
            )

        if self.config.show_username:
            output += (
                add_styles(getuser(), self.config.colours.username, BasicStyle.BOLD)
                + ":"
            )

        # resolve the cwd if the user deletes it
        while not self.cwd.exists():
            self.cwd = self.cwd.parent

        # fixes capitilization of cwd
        self.cwd = self.cwd.resolve()

        if self.config.shorten_path:
            if self.cwd == Path.home():
                output += add_styles(
                    "~", self.config.colours.current_path, BasicStyle.BOLD
                )
            elif self.cwd.is_relative_to(Path.home()):
                relative_path = self.cwd.relative_to(Path.home())
                relative_path_string = relative_path.as_posix()
                if len(relative_path_string) > self.config.shortened_path_length:
                    output += add_styles(
                        shorten_path(
                            relative_path,
                            self.config.shortened_path_length,
                            "~/.../",
                        ),
                        self.config.colours.current_path,
                        BasicStyle.BOLD,
                    )
                else:
                    output += add_styles(
                        f"~/{relative_path_string}",
                        self.config.colours.current_path,
                        BasicStyle.BOLD,
                    )
            elif len(str(self.cwd)) > self.config.shortened_path_length:
                output += add_styles(
                    shorten_path(
                        self.cwd,
                        self.config.shortened_path_length,
                        f"{Path(Path.home().anchor).as_posix()}.../",
                    ),
                    self.config.colours.current_path,
                    BasicStyle.BOLD,
                )
            else:
                output += add_styles(
                    self.cwd.as_posix(),
                    self.config.colours.current_path,
                    BasicStyle.BOLD,
                )
        else:
            output += add_styles(
                self.cwd.as_posix(),
                self.config.colours.current_path,
                BasicStyle.BOLD,
            )

        return output

    def main(self) -> None:
        while True:
            try:
                try:
                    string_input = input(f"{self.input_string()} $ ").strip()
                except EOFError:
                    continue

                if not string_input:
                    continue

                self.write_history(string_input)

                err = self.interpret_command(string_input)
                if err is not None:
                    print(add_styles(str(err), self.config.colours.errors))
            except KeyboardInterrupt:  # allows the user to exit out of running cmd
                print()
