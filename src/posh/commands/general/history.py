from __future__ import annotations

from collections.abc import Sequence
from functools import cache
from typing import TYPE_CHECKING, Iterator

from loguru import logger
from pyperclip import copy  # type: ignore

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import HistoryManager, Interpreter


def load_history_lines(history_manager: HistoryManager) -> Iterator[str]:
    try:
        with history_manager.get_file("r") as file:
            yield from (line for line in file)
    except OSError as e:
        logger.error(e)
        return


def clear_history(history_manager: HistoryManager) -> None:
    try:
        with history_manager.get_file("w"):
            pass
    except OSError as err:
        logger.error(err)

    get_line.cache_clear()


@cache
def get_line(line_number: int, history_manager: HistoryManager) -> str | IndexError:
    # if using negative indexes we have to substract one to account for the current command
    if line_number < 0:
        line_number -= 1

    lines = tuple(load_history_lines(history_manager))

    if len(lines) < line_number:
        return IndexError(
            f"Error: index out of range, index {line_number}, range {len(lines) - 1}"
        )
    return lines[line_number].strip()


class History(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_mutually_exclusive_group().add_argument(
            "-p",
            "--print",
            action="store_true",
            help="print the history",
        )
        self.parser.add_mutually_exclusive_group().add_argument(
            "-cp",
            "--copy",
            type=int,
            help="copy the given line number (supports negative indexes)",
        )
        self.parser.add_mutually_exclusive_group().add_argument(
            "-c",
            "--clear",
            action="store_true",
            help="clear the history",
        )

    @classmethod
    def command(cls) -> str:
        return "history"

    @staticmethod
    def description() -> str:
        return "Manage the console's command history"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return None

        if console.history_manager is None:
            return Exception("Error: couldn't load history manager")

        if options.print or all(not arg for arg in vars(options).values()):
            for index, cmd in enumerate(load_history_lines(console.history_manager)):
                print(f"{index:<5}  {cmd}", end="")
        elif options.clear:
            clear_history(console.history_manager)
        elif options.copy:
            line = get_line(options.copy, console.history_manager)

            if isinstance(line, Exception):
                return line

            copy(line)

        return None
