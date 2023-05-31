from typing import Any


def print_dict(
    d: dict[str, Any], seperator: str = "=", whitespace: str = "    ", depth: int = 0
) -> None:
    current_whitespace = whitespace * depth
    for key, value in d.items():
        if isinstance(value, dict):
            print(f"{current_whitespace}{key}:")
            print_dict(value, seperator, whitespace, depth + 1)  # type: ignore
        else:
            print(f"{current_whitespace}{key}{seperator}{value}")
