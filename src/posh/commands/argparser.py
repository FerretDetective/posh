from __future__ import annotations

from argparse import ArgumentError, ArgumentParser, ArgumentTypeError, Namespace
from typing import TYPE_CHECKING, Self, Sequence

if TYPE_CHECKING:
    from .command import Command


class InlineArgumentParser(ArgumentParser):
    @classmethod
    def from_command(cls, command: Command) -> Self:
        parser = cls(
            prog=command.command(),
            description=command.description(),
            exit_on_error=False,
        )
        return parser

    def parse_arguments(self, args: Sequence[str]) -> Namespace | None:
        try:
            return self.parse_args(args)
        except ArgumentError as e:
            print(f"Error: {e}")
        except SystemExit:
            pass
        return None

    def parse_known_arguments(
        self, args: Sequence[str]
    ) -> tuple[Namespace, list[str]] | None:
        try:
            return self.parse_known_args(args)
        except ArgumentTypeError as e:
            print(f"Error: {e}")
        except SystemExit:
            pass
        return None
