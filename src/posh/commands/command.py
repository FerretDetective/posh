from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..interpreter import Interpreter


class Command(ABC):
    __slots__ = ()

    @classmethod
    @abstractmethod
    def command(cls) -> str:
        ...

    @staticmethod
    @abstractmethod
    def description() -> str:
        ...

    @abstractmethod
    def help(self) -> str:
        ...

    @abstractmethod
    def execute(self, console: Interpreter, args: Sequence[str]) -> None | Exception:
        ...
