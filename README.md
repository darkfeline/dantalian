# Dantalian README

Project Website: <http://darkfeline.github.io/dantalian/>

Dantalian is a Python library to assist file organization and tagging
using hard links.

Comprehensive documentation can be found online at
<http://dantalian.readthedocs.org/en/>

## Features

- Organizes using the plain file system.
- Extremely flexible (no tag limit, no tag naming restrictions,
  hierarchical tags, no file naming restrictions, can tag all files and
  directories).
- Transparent to other applications, since it works directly with the
  file system.

## Requirements

Dantalian works on contiguous POSIX-compatible file systems.  Specific
requirements may vary, but for most Linux users there should not be any
problems.

## Installation

Install using packages from your distribution if available.
Otherwise, see below for manual installation.

### Arch Linux

- [dantalian](https://aur.archlinux.org/packages/dantalian/)
- [dantalian-git](https://aur.archlinux.org/packages/dantalian-git/)

### Manual installation

Dependencies:

- [Python 3](http://www.python.org/)
- [GNU findutils](http://www.gnu.org/software/findutils/)

Build dependencies:

- [setuptools](https://pypi.python.org/pypi/setuptools)
- [Sphinx](http://sphinx-doc.org/index.html)

Installation is simple.  Obtain the sources, then run:

    $ python setup.py install

This will most likely require root, and will install Dantalian globally
on the system.  Otherwise, you can use virtualenv, or install it for the
user:

    $ python setup.py install --user

By default this will install to `~/.local/bin`.

## Usage

Dantalian can be used either as a Python library or a standalone program.

Note that using Dantalian separately may be slow due to Python's nature.
When performing bulk operations, consider using Dantalian as a library
in a Python script instead of invoking Dantalian repeated in a shell
script.

Check the documentation for more information.
