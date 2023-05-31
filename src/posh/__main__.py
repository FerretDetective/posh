from argparse import ArgumentParser
from os import truncate
from pathlib import Path

from loguru import logger

from . import __version__
from .colours import TextStyle, add_styles
from .interpreter import Console, FileIntepreter


@logger.catch
def main() -> None:
    try:
        truncate(Path(__file__).parent / "data" / "posh.log", 0)
    except FileNotFoundError:
        pass
    logger.remove()
    logger.add(
        Path(__file__).parent / "data" / "posh.log",
        delay=True,
        enqueue=True,
    )

    parser = ArgumentParser()
    parser.add_mutually_exclusive_group().add_argument(
        "file_path", nargs="?", default=None, type=str, help="file to interpret"
    )
    parser.add_argument(
        "-d",
        "--starting_directory",
        type=str,
        default="",
        help="starting directory",
    )

    arguments = parser.parse_args()

    if not arguments.starting_directory:
        starting_directory = Path.home()
    else:
        starting_directory = Path(arguments.starting_directory).expanduser().resolve()
        if not starting_directory.exists():
            print(
                add_styles(
                    f"invalid starting directory: {arguments.starting_directory!r}",
                    TextStyle.LIGHT_RED,
                )
            )
            return

    if arguments.file_path is not None:
        file_path = Path(arguments.file_path)

        if not file_path.is_absolute():
            file_path = starting_directory / file_path

        file_path.expanduser().resolve()

        if not file_path.is_file():
            print(
                add_styles(
                    f"invalid file or path: {arguments.file_path!r}",
                    TextStyle.LIGHT_RED,
                )
            )
            return

        interpreter = FileIntepreter(Path(starting_directory), file_path)
    else:
        print(
            f"posh {__version__}  Copyright (C) 2023  Eris Fletcher\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details type 'license -p'.\n"
            "This is free software, and you are welcome to redistribute it\n"
            "under certain conditions; for details type 'license -p'.\n"
        )
        interpreter = Console(Path(starting_directory))

    interpreter.main()


if __name__ == "__main__":
    main()
