from typing import Callable, Mapping, TypeVar

KT = TypeVar("KT")
VT = TypeVar("VT")


def print_dict(
    d: Mapping[KT, VT],
    format_key: Callable[[KT], str] = str,
    format_val: Callable[[VT], str] = str,
    seperator: str = "=",
    whitespace: str = " " * 4,
    depth: int = 0,
) -> None:
    current_whitespace = whitespace * depth
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{current_whitespace}{format_key(key)}:")
            print_dict(
                value,  # type: ignore
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
