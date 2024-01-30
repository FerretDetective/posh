from argparse import ArgumentParser
from pathlib import Path

from loguru import logger

from . import __version__
from .colours import FgColour, add_colours
from .commands.file_system.path_utils import parse_path
from .interpreter import Console, FileIntepreter
from .interpreter.interpreter import Interpreter


@logger.catch
def main() -> None:
    logger.remove()
    logger.add(
        Path(__file__).parent / "data" / "posh.log",
        delay=True,
        enqueue=True,
        level="WARNING",
    )

    parser = ArgumentParser(prog="posh")
    parser.add_mutually_exclusive_group().add_argument(
        "-v",
        "--version",
        action="store_true",
        default=False,
        help="print the interpreter version and exit",
    )
    parser.add_mutually_exclusive_group().add_argument(
        "file_path", nargs="?", default=None, type=str, help="file to interpret"
    )
    parser.add_argument(
        "-d",
        "--starting_directory",
        type=str,
        default=Path.cwd(),
        help="starting directory",
    )

    arguments = parser.parse_args()

    if arguments.version:
        print(__version__)
        return

    starting_directory: str | Path = arguments.starting_directory
    if not isinstance(starting_directory, Path):
        starting_directory = parse_path(starting_directory, Path.cwd())

        if not starting_directory.exists():
            print(
                add_colours(
                    f"invalid starting directory: {arguments.starting_directory!r}",
                    FgColour.LIGHT_RED,
                )
            )
            return

    interpreter: Interpreter
    if arguments.file_path is not None:
        file_path = parse_path(arguments.file_path, Path.cwd())

        if not file_path.is_file():
            print(
                add_colours(
                    f"invalid file or path: {arguments.file_path!r}",
                    FgColour.LIGHT_RED,
                )
            )
            return

        interpreter = FileIntepreter(starting_directory, file_path)
    else:
        print(
            f"posh {__version__}  Copyright (C) 2023  Eris\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details type 'license -p'.\n"
            "This is free software, and you are welcome to redistribute it\n"
            "under certain conditions; for details type 'license -p'.\n"
        )
        interpreter = Console(starting_directory)

    interpreter.main()


if __name__ == "__main__":
    main()
