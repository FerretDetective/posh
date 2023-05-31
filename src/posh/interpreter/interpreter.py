from __future__ import annotations

from os import getpid
from pathlib import Path

from loguru import logger

from .commands import (
    ExecutableCommand,
    VariableDeclaration,
    VariableReference,
    load_commands,
    parse_command,
)
from .config import Config
from .history_manager import HistoryManager


class UnknownCommand(Exception):
    ...


class Interpreter:
    def __init__(self, starting_directory: Path) -> None:
        self.cwd = starting_directory
        self.variables = dict[str, str]()
        self.project_dir = Path(__file__).parent.parent
        self.data_directory = self.project_dir / "data"
        if not self.data_directory.exists():
            self.data_directory = None
            logger.warning("data directory couldn't be found")
            self.config = Config()
            self.history_manager = None
        else:
            self.config = Config.from_json(self.data_directory / "config.json")

            if (history_path := self.data_directory / "history.txt").exists():
                self.history_manager = HistoryManager(history_path)
            else:
                try:
                    history_path.touch()
                    self.history_manager = HistoryManager(history_path)
                except OSError as err:
                    logger.error(f"couldn't create history file, {err}")
                    self.history_manager = None
        self.commands = load_commands(self.config.aliases, self.config.colours.errors)

    def __repr__(self) -> str:
        return f"{type(self).__name__}{{pid: {getpid()!r}, cwd: {self.cwd!r}}}"

    def reload_config(self) -> None:
        if self.data_directory is None:
            self.config = Config()
        else:
            self.config = Config.from_json(self.data_directory / "config.json")

    def write_history(self, cmd: str) -> None:
        if not self.config.record_history or self.history_manager is None:
            return
        self.history_manager.add(cmd)

    def interpret_command(self, string_command: str) -> None | Exception:
        commands = parse_command(string_command)

        if isinstance(commands, ValueError):
            return commands

        for command in commands:
            if isinstance(command, VariableDeclaration):
                self.variables[command.name] = command.value
            elif isinstance(command, VariableReference):
                if (variable := self.variables.get(command.name)) is None:
                    return Exception(f"Error: unknown variable {command.name!r}")

                print(repr(variable) if " " in variable else variable)
            elif isinstance(command, ExecutableCommand):
                if (executor := self.commands.get(command.command)) is None:
                    return UnknownCommand(f"Error: unknown command {command.command!r}")

                for index, value in enumerate(command.args):
                    if value.startswith("$"):
                        variable = self.variables.get(value)
                        if variable is None:
                            return Exception(f"Error: unknown variable {value!r}")
                        command.args[index] = (
                            repr(variable) if " " in variable else variable
                        )

                if (err := executor().execute(self, command.args)) is not None:
                    return err

        return None
