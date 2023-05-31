from typing import Any, Callable


def print_dict(
    d: dict[str, Any],
    format_func: Callable[[object], str] = str,
    seperator: str = "=",
    whitespace: str = "    ",
    depth: int = 0,
) -> None:
    current_whitespace = whitespace * depth
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{current_whitespace}{format_func(key)}:")
            print_dict(value, format_func, seperator, whitespace, depth + 1)  # type: ignore
        else:
            print(
                f"{current_whitespace}{format_func(key)}{seperator}{format_func(value)}"
            )
