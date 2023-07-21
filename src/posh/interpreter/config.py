from __future__ import annotations

from json import dump, load
from pathlib import Path
from shlex import shlex
from string import whitespace
from typing import Any, Self, cast

from loguru import logger

from ..colours import FgColour, add_colours


class ColourConfig:
    def __init__(
        self,
        time: str | None = None,
        current_path: str | None = None,
        user_name: str | None = None,
        directory_path: str | None = None,
        file_path: str | None = None,
        errors: str | None = None,
    ) -> None:
        # if anything is None it should use the default
        defaults = self.get_defaults()
        self.time = self.parse_string(time) or defaults[0]
        self.current_path = self.parse_string(current_path) or defaults[1]
        self.username = self.parse_string(user_name) or defaults[2]
        self.directory_path = self.parse_string(directory_path) or defaults[3]
        self.file_path = self.parse_string(file_path) or defaults[4]
        self.errors = self.parse_string(errors) or defaults[5]

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.time}, {self.current_path}, {self.username}, "
            f"{self.directory_path}, {self.file_path}, {self.errors}"
        )

    @staticmethod
    def get_defaults() -> (
        tuple[FgColour, FgColour, FgColour, FgColour, FgColour, FgColour]
    ):
        # define all default colours here
        return (
            FgColour.WHITE,
            FgColour.LIGHT_BLUE,
            FgColour.WHITE,
            FgColour.LIGHT_CYAN,
            FgColour.GREEN,
            FgColour.LIGHT_RED,
        )

    def set_default(self) -> None:
        (
            self.time,
            self.current_path,
            self.username,
            self.directory_path,
            self.file_path,
            self.errors,
        ) = self.get_defaults()

    def parse_string(self, string: str | None) -> FgColour | None:
        if string is None:
            return None

        if not hasattr(FgColour, string):
            print(add_colours(f"Error: invalid colour {string!r}", self.errors))
            return None

        return cast(FgColour, getattr(FgColour, string))


class Config:
    def __init__(
        self,
        path: Path,
        show_time: bool | None = None,
        show_username: bool | None = None,
        record_history: bool | None = None,
        shorten_path: bool | None = None,
        shortened_path_length: int | None = None,
        colours: dict[str, str] | None = None,
        aliases: dict[str, str] | None = None,
    ) -> None:
        # if anything is None it should use the default
        defaults = self.get_defaults()
        self.path = path
        self.show_time = show_time if show_time is not None else defaults[0]
        self.show_username = show_username if show_username is not None else defaults[1]
        self.record_history = (
            record_history if record_history is not None else defaults[2]
        )
        self.shorten_path = shorten_path if shorten_path is not None else defaults[3]
        self.shortened_path_length = shortened_path_length or defaults[4]
        self.colours = ColourConfig(**colours) if colours is not None else defaults[5]
        self.aliases = (
            self.parse_aliases(aliases) if aliases is not None else defaults[6]
        )

        self.check_aliases()

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.path!r}, {self.show_time}, {self.show_username}, "
            f"{self.record_history}, {self.shorten_path}, {self.shortened_path_length}, "
            f"{self.colours!r}, {self.aliases!r})"
        )

    @classmethod
    def from_json(cls, path: Path) -> Self:
        try:
            with open(path, "r", encoding="utf8") as file:
                data: dict[Any, Any] = load(file)
        except OSError as err:
            logger.error(f"failed to open config file @ {path!r}, {err=!r}")
            return cls(path)

        try:
            return cls(path, **data)
        except TypeError as err:
            self = cls(path)
            logger.error(f"failed to create config with {data!r}, {err=!r}")
            print(add_colours("Error: invalid config", self.colours.errors))
            return self

    @staticmethod
    def get_defaults() -> (
        tuple[bool, bool, bool, bool, int, ColourConfig, dict[str, list[str]]]
    ):
        # define all defaults for this class here
        return (True, True, True, True, 40, ColourConfig(), {})

    def set_defaults(self) -> None:
        (
            self.show_time,
            self.show_username,
            self.record_history,
            self.shorten_path,
            self.shortened_path_length,
            self.colours,
            self.aliases,
        ) = self.get_defaults()

    def as_dict(self) -> dict[str, Any]:
        return {
            "show_time": self.show_time,
            "show_username": self.show_username,
            "record_history": self.record_history,
            "shorten_path": self.shorten_path,
            "shortened_path_length": self.shortened_path_length,
            "colours": {
                "time": self.colours.time.name,
                "current_path": self.colours.current_path.name,
                "user_name": self.colours.username.name,
                "directory_path": self.colours.directory_path.name,
                "file_path": self.colours.file_path.name,
                "errors": self.colours.errors.name,
            },
            "aliases": {alias: " ".join(arg) for alias, arg, in self.aliases.items()},
        }

    def write_to_json(self) -> None:
        try:
            with open(self.path, "w", encoding="utf8") as file:
                dump(self.as_dict(), file, indent=4)
        except OSError as err:
            logger.error(f"failed to save config, {err}")
            print(add_colours("failed to save config", self.colours.errors))

    def check_aliases(self) -> None:
        to_remove = list[str]()
        for alias in self.aliases:
            if any(s in alias for s in whitespace):
                print(
                    add_colours(
                        f"Error: alias {alias!r} is invalid, white cannot be used in alias keys",
                        self.colours.errors,
                    )
                )
                to_remove.append(alias)

        for key in to_remove:
            self.aliases.pop(key)

    def parse_aliases(self, aliases: dict[str, str]) -> dict[str, list[str]]:
        parsed_aliases: dict[str, list[str]] = {}
        for alias, args in aliases.items():
            lexer = shlex(args)
            lexer.whitespace_split = True

            try:
                parsed_aliases[alias] = list(lexer)
            except ValueError as err:
                print(
                    add_colours(
                        f"Error: failed to create alias {alias!r}, {err}",
                        self.colours.errors,
                    )
                )
                continue
        return parsed_aliases
