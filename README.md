# Posh Shell

Version: 1.1.0

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Links](#links)
- [Overview](#overview)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [License](#license)

## Links

- [Home Page](https://github.com/ErisFletcher/posh)
- [Issue Tracker](https://github.com/ErisFletcher/posh/issues)

## Overview

The posh shell is a cross platform shell written in python meant to be a partial substitute for
other shells like bash, zsh, powershell, etc. It implements many of the commands like 'mv', 'rm',
'cp', etc, and if the command hasn't yet been implemented, you can access your operating system's
underlying shell using the 'run' command.

## Installation

1. Download the project
2. Open your terminal in the install location of the shell
3. Run `$ python posh/setup.py` or `$ python -m pip install -r posh/requirements.txt`

## Basic Usage

### Running the shell as in interactive mode

1. Open your terminal in the install location of the shell
2. Run `$ python -m posh <...args>` to start the interpreter

### Running a script with the shell

1. Open your terminal in the install location of the shell
2. Run `$ python -m posh <path-to-your-script> <...args>`

If you need help with any commands when in the shell run `$ help <cmd>` or `$ cmd --help` to print
the help page.

## License

This project is licensed with the GNU General Public License V3, for more information view the
license file which can be located by running `$ license -w` or run `$ license -p` to print the
license.
