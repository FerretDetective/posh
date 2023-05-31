from .command import Executable
from .file_system import Cat, Cd, Cp, Ls, Mkdir, Mv, Pwd, Rm, Rmdir, Touch
from .general import Alias, Clear, Config, Exit, Help, History, License
from .processes import Kill, Ps, Run

__all__ = ("Executable",)

COMMANDS: list[type[Executable]] = [
    Exit,
    Clear,
    Cd,
    Help,
    History,
    Pwd,
    Ls,
    Cat,
    Touch,
    Rm,
    Rmdir,
    Mkdir,
    Cp,
    Config,
    Mv,
    Ps,
    Run,
    Kill,
    Alias,
    License,
]
