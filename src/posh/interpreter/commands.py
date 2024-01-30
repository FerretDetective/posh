from __future__ import annotations

from dataclasses import dataclass
from shlex import shlex
from typing import TYPE_CHECKING, Mapping, Sequence

from ..commands import COMMANDS

if TYPE_CHECKING:
    from ..commands import Executable


class FailedToParseError(Exception):
    pass


@dataclass
class Command:
    full_args: list[str]


@dataclass
class ExecutableCommand(Command):
    command: str
    args: list[str]


@dataclass
class VariableReference(Command):
    name: str


@dataclass
class VariableDeclaration(Command):
    name: str
    value: str


def expand_aliases(
    command_groups: list[list[str]],
    aliases: Mapping[str, list[str]],
) -> list[list[str]]:
    for cmd_group_index, cmd_group in enumerate(command_groups):
        if cmd_group and "alias" == cmd_group[0]:
            continue

        aliases_copy = dict(aliases)
        for _ in range(len(aliases_copy)):
            cur_group: list[str] = []
            indexs_to_replace: list[tuple[int, list[str]]] = []
            for inner_index, arg in enumerate(cmd_group):
                if " " in arg:
                    continue

                cur_group.append(arg)

                if arg in aliases_copy:
                    expanded = aliases_copy[arg]
                    if expanded != cur_group:
                        indexs_to_replace.append((inner_index, expanded))
                        del aliases_copy[arg]
                    cur_group = []

            for inner_index, args in indexs_to_replace:
                cmd_group = (
                    cmd_group[:inner_index] + args + cmd_group[inner_index + 1 :]
                )
                command_groups[cmd_group_index] = cmd_group
    return command_groups


def parse_commands(commands: Sequence[list[str]]) -> list[Command] | Exception:
    command_strings = list[Command]()
    for arg_group in commands:
        if not arg_group:
            return FailedToParseError("Error: failed to parse command")

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


def parse_string_command(
    string_args: str, aliases: Mapping[str, list[str]]
) -> list[Command] | Exception:
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

    return parse_commands(expand_aliases(cmd_groups, aliases))


def load_commands() -> dict[str, type[Executable]]:
    return {command.command(): command for command in COMMANDS}
