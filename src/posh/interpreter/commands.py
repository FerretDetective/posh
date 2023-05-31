from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from shlex import shlex
from typing import TYPE_CHECKING

from ..colours import TextStyle, add_styles
from ..commands import COMMANDS

if TYPE_CHECKING:
    from ..commands import Command


@dataclass
class CommandString:
    full_args: list[str]


@dataclass
class ExecutableCommand(CommandString):
    command: str
    args: list[str]


@dataclass
class VariableReference(CommandString):
    name: str


@dataclass
class VariableDeclaration(CommandString):
    name: str
    value: str


@cache
def parse_command(string_args: str) -> list[CommandString] | ValueError:
    lexer = shlex(string_args, punctuation_chars=True, posix=True)
    lexer.whitespace_split = True

    try:
        args = list(lexer)
    except ValueError as err:
        return ValueError(f"Error: {err}")

    cmd_groups = list[list[str]]()
    cur_args = list[str]()
    for arg in args:
        if ";" in arg:
            cmd_groups.append(cur_args)
            cur_args = list[str]()
            continue
        cur_args.append(arg.replace("'", "").replace('"', ""))

    if cur_args:
        cmd_groups.append(cur_args)  # remove remaing arguments left over

    command_strings = list[CommandString]()
    for arg_group in cmd_groups:
        if arg_group[0].startswith("$"):
            if "=" in arg_group:
                if len(arg_group) != 3:
                    return ValueError(
                        f"Error: syntax error, invalid variable declaration: {' '.join(arg_group)}"
                    )

                command_strings.append(
                    VariableDeclaration(arg_group, arg_group[0], arg_group[-1])
                )
            else:
                if len(arg_group) != 1:
                    return ValueError(
                        f"Error: syntax error, invalid variable reference: {' '.join(arg_group)}"
                    )

                command_strings.append(VariableReference(arg_group, arg_group[0]))
        else:
            command_strings.append(
                ExecutableCommand(arg_group, arg_group[0], arg_group[1:])
            )

    return command_strings


def load_commands(
    aliases: dict[str, str], err_style: TextStyle
) -> dict[str, type[Command]]:
    commands = {command.command(): command for command in COMMANDS}

    for alias, cmd_str in aliases.items():
        command = commands.get(cmd_str)
        if command is None:
            print(
                add_styles(
                    f"Error: invalid alias: {alias!r} -> {cmd_str!r}, {cmd_str} does not exist",
                    err_style,
                )
            )
            continue
        commands[alias] = command

    return commands
