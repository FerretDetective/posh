from __future__ import annotations

from functools import cache
from getpass import getuser
from os import get_terminal_size
from pathlib import Path
from time import strftime

from ..colours import Meta, add_colours
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


class Console(Interpreter):
    def input_string(self) -> str:
        output = ""

        if self.config.show_time:
            time_block = f"[{strftime('%X')}]"
            output += add_colours(
                f"{time_block:>{get_terminal_size().columns}}\r",
                self.config.colours.time,
                Meta.BOLD,
            )

        if self.config.show_username:
            output += (
                add_colours(getuser(), self.config.colours.username, Meta.BOLD) + ":"
            )

        # resolve the cwd if the user deletes it
        while not self.cwd.exists():
            self.cwd = self.cwd.parent

        # fixes capitilization of cwd
        self.cwd = self.cwd.resolve()

        if self.config.shorten_path:
            if self.cwd == Path.home():
                output += add_colours("~", self.config.colours.current_path, Meta.BOLD)
            elif self.cwd.is_relative_to(Path.home()):
                relative_path = self.cwd.relative_to(Path.home())
                relative_path_string = relative_path.as_posix()
                if len(relative_path_string) > self.config.shortened_path_length:
                    output += add_colours(
                        shorten_path(
                            relative_path,
                            self.config.shortened_path_length,
                            "~/.../",
                        ),
                        self.config.colours.current_path,
                        Meta.BOLD,
                    )
                else:
                    output += add_colours(
                        f"~/{relative_path_string}",
                        self.config.colours.current_path,
                        Meta.BOLD,
                    )
            elif len(str(self.cwd)) > self.config.shortened_path_length:
                output += add_colours(
                    shorten_path(
                        self.cwd,
                        self.config.shortened_path_length,
                        f"{Path(Path.home().anchor).as_posix()}.../",
                    ),
                    self.config.colours.current_path,
                    Meta.BOLD,
                )
            else:
                output += add_colours(
                    self.cwd.as_posix(),
                    self.config.colours.current_path,
                    Meta.BOLD,
                )
        else:
            output += add_colours(
                self.cwd.as_posix(),
                self.config.colours.current_path,
                Meta.BOLD,
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
                    print(add_colours(str(err), self.config.colours.errors))
            except KeyboardInterrupt:  # allows the user to exit out of running cmd
                print()
