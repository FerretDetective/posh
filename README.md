# Posh Shell

Version: 1.2.0

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Links](#links)
- [Overview](#overview)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [License](#license)

## Links

- [Home Page](https://github.com/FerretDetective/posh)
- [Issue Tracker](https://github.com/FerretDetective/posh/issues)

## Overview

The posh shell is a cross platform shell written in python meant to be a partial substitute for other shells like bash, zsh, powershell, etc. It implements many of the commands like 'mv', 'rm', 'cp', etc, and if the command hasn't yet been implemented, you can access your operating system's underlying shell using the 'run' command.

## Installation

### Installing with git

1. Open your terminal.
2. Run `$ python -m pip install git+https://github.com/FerretDetective/posh`.

### Installing without git

1. Open the github page located [here](https://github.com/FerretDetective/posh).
2. Find the green "Code" button and click on it.
3. In the pop up, move down and click on "Download Zip".
4. Open your downloads folder.
5. Extract the downloaded zip.
6. Move the extracted folder to where you would like the install location to be.
7. Open your terminal.
8. Run `$ cd <path to the extracted folder>`.
9. Run `$ ls` for Unix systems and `$ dir` for Windows/Dos systems and make sure you see the "src" folder.
10. Run `$ python -m pip install .`.

## Basic Usage

### Running the Shell in Interactive Mode

To start the interpreter run `$ python -m posh <...args>` in your terminal.

### Running a Script with the Shell

To start the interpreter run `$ python -m posh <path-to-your-script> <...args>` in your terminal.

### Getting Help

If you need help with any commands when in the shell run `$ help <cmd>` or `$ <cmd> --help` to print the help page.

## License

This project is licensed with the GNU General Public License V3, for more information view the license file which can be accessed on github located [here](https://github.com/FerretDetective/posh/blob/main/LICENSE.md) by running `$ license -w` or run `$ license -p` to print the license.
