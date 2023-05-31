from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ...colours import TextStyle, add_styles
from ..argparser import InlineArgumentParser
from ..command import Executable
from .print_utils import print_dict

if TYPE_CHECKING:
    from ...interpreter import Interpreter


class Config(Executable):
    def __init__(self) -> None:
        self.parser = InlineArgumentParser.from_command(self)
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "-p",
            "--print",
            action="store_true",
            help="print the console's current config",
        )
        group.add_argument(
            "-gd",
            "--generate_default",
            action="store_true",
            help="generate a default config file and reload the console",
        )
        group.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help="reset the currently loaded config to the default",
        )
        group.add_argument(
            "-w",
            "--where",
            action="store_true",
            help="print the location of the config file",
        )
        group.add_argument(
            "-pc",
            "--print_colours",
            action="store_true",
            help="print the availible colours to configure the console with",
        )
        group.add_argument(
            "-R",
            "--reload",
            action="store_true",
            help="reload the console's config after applying changes directly to the file",
        )
        group.add_argument(
            "-s",
            "--save",
            action="store_true",
            help="apply all changes, then save the current config to the config file",
        )

        bool_str = ("true", "false")
        self.parser.add_argument(
            "--show_time",
            choices=bool_str,
            help="toggle whether to show the current time in the regional format",
        )
        self.parser.add_argument(
            "--show_username",
            choices=bool_str,
            help="toggle whether to show the username next to the console's cwd",
        )
        self.parser.add_argument(
            "--record_history",
            choices=bool_str,
            help="toggle the recording of the console history",
        )
        self.parser.add_argument(
            "--shorten_path",
            choices=bool_str,
            help="toggle whether or not to shorten the path in the console's cwd",
        )
        self.parser.add_argument(
            "--shortened_path_length",
            type=int,
            help="length to shorten the console's cwd path to",
        )

        colour_choices = [colour.name for colour in TextStyle]
        self.parser.add_argument(
            "--time_colour",
            choices=colour_choices,
            help="change the console time display's colour",
        )
        self.parser.add_argument(
            "--current_path_colour",
            choices=colour_choices,
            help="change the console's cwd path colour",
        )
        self.parser.add_argument(
            "--username_colour",
            choices=colour_choices,
            help="change the console's username colour",
        )
        self.parser.add_argument(
            "--directory_name_colour",
            choices=colour_choices,
            help="change the console's directory name colour",
        )
        self.parser.add_argument(
            "--file_path_colour",
            choices=colour_choices,
            help="change the console's file path colour",
        )
        self.parser.add_argument(
            "--error_colour",
            choices=colour_choices,
            help="change the console's error colour",
        )

    @classmethod
    def command(cls) -> str:
        return "config"

    @staticmethod
    def description() -> str:
        return "Manage the console's configurations"

    def help(self) -> str:
        return self.parser.format_help()

    def execute(self, console: Interpreter, args: Sequence[str]) -> None:
        if (options := self.parser.parse_arguments(args)) is None:
            return

        if all(not arg for arg in vars(options).values()):
            self.parser.print_usage()
            return

        if options.show_time is not None:
            console.config.show_time = options.show_time == "true"

        if options.show_username is not None:
            console.config.show_username = options.show_username == "true"

        if options.record_history is not None:
            console.config.record_history = options.record_history == "true"

        if options.shorten_path is not None:
            console.config.shorten_path = options.shorten_path == "true"

        if options.shortened_path_length is not None:
            console.config.shortened_path_length = options.shortened_path_length

        if options.time_colour is not None:
            colour_string = options.time_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.time = colour

        if options.current_path_colour is not None:
            colour_string = options.current_path_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.current_path = colour

        if options.username_colour is not None:
            colour_string = options.username_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.username = colour

        if options.directory_name_colour is not None:
            colour_string = options.directory_name_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.directory_path = colour

        if options.file_path_colour is not None:
            colour_string = options.file_path_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.file_path = colour

        if options.error_colour is not None:
            colour_string = options.error_colour
            colour = console.config.colours.parse_string(colour_string)

            if colour is not None:
                console.config.colours.errors = colour

        if options.print:
            print_dict(console.config.as_dict())

        if options.print_colours:
            for colour in TextStyle:
                print(add_styles(colour.name, colour))

        if options.where:
            if console.config.path is None:
                print("The config file was not found")
            else:
                path_str = console.config.path.as_posix()
                print(
                    add_styles(
                        repr(path_str) if " " in path_str else path_str,
                        console.config.colours.file_path,
                    )
                )

        if options.reload:
            console.reload_config()

        if options.save:
            console.config.write_to_json()

        if options.reset:
            console.config.set_defaults()

        if options.generate_default:
            console.config.set_defaults()
            console.config.write_to_json()
