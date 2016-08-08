# Dantalian README

Project Website: <http://darkfeline.github.io/dantalian/>

Dantalian is a Python 3 library to assist file organization and tagging
using hard links.

Comprehensive documentation can be found online at
<http://dantalian.readthedocs.io/>

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

Build dependencies:

- [setuptools](https://pypi.python.org/pypi/setuptools)
- [Sphinx](http://sphinx-doc.org/index.html) (for documentation)

Installation is simple.  Obtain the sources, then run:

    $ python setup.py install

This will most likely require root, and will install Dantalian globally
on the system.  Otherwise, you can use virtualenv, or install it for the
user:

    $ python setup.py install --user

By default this will install to `~/.local/bin`.

It is recommended to install the man pages as well.  The man pages can
be built like so:

    $ cd doc
    $ make man

The man pages can be found in `doc/_build/man`.  How they are
installed depends on your system.  On Arch Linux, man pages are
installed in `/usr/share/man` as gzipped archives, so you would do
the following:

    $ cd doc/_build/man
    $ gzip ./*
    # install ./* /usr/share/man/man1

## Usage

Dantalian can be used either as a Python library or a standalone program.

Note that using Dantalian separately may be slow due to Python's nature.
When performing bulk operations, consider using Dantalian as a library
in a Python script instead of invoking Dantalian repeatedly in a shell
script.

Check the documentation for more information.
