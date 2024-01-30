from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from psutil import AccessDenied, Process, process_iter

from ..argparser import InlineArgumentParser
from ..command import Executable

if TYPE_CHECKING:
    from ...interpreter import Interpreter


def get_pid(process: Process) -> str:
    try:
        return str(process.pid)
    except AccessDenied:
        return "N/A"


def get_tty(process: Process) -> str:
    try:
        return process.terminal()  # type: ignore
    except (AccessDenied, AttributeError):
        return "N/A"


def get_time(process: Process) -> str:
    try:
        times = process.cpu_times()
    except AccessDenied:
        return "N/A"
    return datetime.fromtimestamp((times.user + times.system) / 1000).strftime("%X")


def get_cmdline(process: Process) -> str:
    try:
        return (
            " ".join((repr(cmd) if " " in cmd else cmd) for cmd in process.cmdline())
            or "N/A"
        )
    except AccessDenied:
        return "N/A"


def format_process(process: Process) -> str:
    info = (get_pid(process), get_tty(process), get_time(process), get_cmdline(process))
    if all(i == "N/A" for i in info):
        return ""
    return f"{info[0]:>5} {info[1]:<8} {info[2]:>8} {info[3]}\n"


class Ps(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)

    @classmethod
    def command(cls) -> str:
        return "ps"

    @staticmethod
    def description() -> str:
        return "Report a snapshot of currently running processes"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if self.parser.parse_arguments(args) is None:
            return

        print(f"  PID TTY{' ' * 10}TIME COMMAND")
        for process in process_iter():
            print(format_process(process), end="")
