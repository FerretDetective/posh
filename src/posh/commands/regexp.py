from re import Pattern
from re import compile as re_compile
from re import error


def compile_regexp(string: str) -> Pattern[str] | error:
    try:
        return re_compile(string.replace("'", "").replace('"', ""))
    except error as e:
        return e
