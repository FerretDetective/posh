from __future__ import annotations

from functools import cache
from shlex import shlex
from typing import TYPE_CHECKING

from ..colours import TextStyle, add_styles
from ..commands import COMMANDS

if TYPE_CHECKING:
    from ..commands import Command


@cache
def parse_command(string_args: str) -> list[list[str]] | ValueError:
    lexer = shlex(string_args, punctuation_chars=True, posix=True)
    lexer.whitespace_split = True

    try:
        args = list(lexer)
    except ValueError as err:
        return ValueError(f"Error: {err}")

    cmd_groups = list[list[str]]()
    cur_args = list[str]()
    for arg in args:
        if arg == ";":
            cmd_groups.append(cur_args)
            cur_args = list[str]()
            continue
        cur_args.append(arg.replace("'", "").replace('"', ""))

    if cur_args:
        cmd_groups.append(cur_args)  # remove remaing arguments left over

    return cmd_groups


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
