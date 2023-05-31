from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from psutil import AccessDenied, NoSuchProcess, Process

from ..argparser import InlineArgumentParser
from ..command import Command

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Kill(Command):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        self.parser.add_argument("pid", type=int, help="pid of the process to kill")
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="kill instead of terminating the process",
        )

    @classmethod
    def command(cls) -> str:
        return "kill"

    @staticmethod
    def description() -> str:
        return "Kill or terminate process with a given pid"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        try:
            process = Process(pid=options.pid)
        except NoSuchProcess:
            return Exception(f"Error: no such process with pid {options.pid}")
        except OverflowError:
            return OverflowError(f"Error: integer too large {options.pid}")

        try:
            if options.force:
                process.kill()
            else:
                process.terminate()
        except AccessDenied:
            return Exception(
                f"Error: access denied, cannot kill process with pid {options.pid}"
            )
        except NoSuchProcess:
            return Exception(
                f"Error: process with pid {options.pid} no longer exists",
            )
