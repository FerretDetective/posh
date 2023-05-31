"""Used to check to see if you can colourize and if the stream needs to be wrapped."""
from os import environ, name
from sys import __stderr__, __stdout__
from typing import Any, TextIO

from .ansi_styles import AnsiStyle, BasicStyle


def should_colourize(stream: Any) -> bool:
    """Check to see if a stream if can be colourized."""
    if stream is __stdout__ or stream is __stderr__:
        if "PYCHARM_HOSTED" in environ:
            return True
        if name == "nt" and "TERM" in environ:
            return True

    try:
        return stream.isatty()
    except Exception:
        return False


def should_wrap(stream: Any) -> bool:
    """Check to see if a stream should be wrapped in a Ansi to Win32 converter."""

    if not should_colourize(stream):
        return False

    from colorama.win32 import winapi_test

    return winapi_test()


def wrap(stream: TextIO):
    """Wrap a stream with a AnsiToWin32 wrapper."""
    from colorama import AnsiToWin32

    return AnsiToWin32(stream, convert=True, strip=False, autoreset=False).stream


def _get_ansi_styles(*styles: AnsiStyle) -> str:
    """Returns the ansi code format in python corresponding to styles given."""

    return "".join(f"\033[{style.value}m" for style in styles)


def add_styles(text: str, *styles: AnsiStyle) -> str:
    """Add styles to text."""
    return _get_ansi_styles(*styles) + text + _get_ansi_styles(BasicStyle.RESET)
