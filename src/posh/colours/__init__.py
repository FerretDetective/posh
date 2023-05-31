"""Package for adding colour(s) and or style(s) to the terminal."""
from .ansi_styles import AnsiStyle, BasicStyle, HighlightStyle, TextStyle
from .colourizer import add_styles, should_colourize, should_wrap, wrap

__all__ = (
    "AnsiStyle",
    "should_colourize",
    "should_wrap",
    "wrap",
    "add_styles",
    "AnsiStyle",
    "BasicStyle",
    "HighlightStyle",
    "TextStyle",
)
