from typing import Callable, Mapping, TypeVar

K = TypeVar("K")
V = TypeVar("V")


def print_dict(
    d: Mapping[K, V],
    format_key: Callable[[K], str] = str,
    format_val: Callable[[V], str] = str,
    seperator: str = "=",
    whitespace: str = " " * 4,
    depth: int = 0,
) -> None:
    current_whitespace = whitespace * depth
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{current_whitespace}{format_key(key)}:")
            print_dict(
                value,
                format_key,
                format_val,
                seperator,
                whitespace,
                depth + 1,
            )
        else:
            print(
                f"{current_whitespace}{format_key(key)}{seperator}{format_val(value)}"
            )
