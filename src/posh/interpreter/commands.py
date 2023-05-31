from __future__ import annotations

from dataclasses import dataclass
from shlex import shlex
from typing import TYPE_CHECKING, Mapping

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


def parse_command(
    string_args: str, aliases: Mapping[str, list[str]]
) -> list[CommandString] | ValueError:
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

    # TODO: verify functionality & refactor for speed + readibility
    for cmd_group_index, cmd_group in enumerate(cmd_groups):
        if "alias" in cmd_group:
            continue

        cur_group: list[str] = []
        indexs_to_replace: list[tuple[int, list[str]]] = []
        for inner_index, arg in enumerate(cmd_group):
            if " " in arg:
                continue

            cur_group.append(arg)

            if arg in aliases:
                expanded = aliases[arg]
                if " ".join(expanded) != " ".join(cur_group):
                    indexs_to_replace.append((inner_index, expanded))
                cur_group = []

        for inner_index, arg in indexs_to_replace:
            cmd_groups[cmd_group_index] = (
                cmd_group[:inner_index] + arg + cmd_group[inner_index + 1 :]
            )

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


def load_commands() -> dict[str, type[Command]]:
    return {command.command(): command for command in COMMANDS}
