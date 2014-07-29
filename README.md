# Dantalian README

Project Website: <http://darkfeline.github.io/dantalian/>

Dantalian is a set of Python scripts to assist file organization and
tagging using hard links.

Comprehensive documentation can be found online at
<http://dantalian.readthedocs.org/en/>

## Features

* Organizes using the plain file system.
* Extremely flexible (no tag limit, no tag naming restrictions,
  hierarchical tags, no file naming restrictions, can tag all files and
  directories).
* Transparent to other applications, since it works directly with the
  file system.

## Requirements

Dantalian works on contiguous POSIX-compatible file systems.  Specific
requirements may vary, but for most Linux users there should not be any
problems.

## Installation

Install using packages from your distribution if available.
Otherwise, see below for manual installation.

* [Arch Linux (AUR)](https://aur.archlinux.org/packages/dantalian/)
* [Arch Linux (AUR) (git)](https://aur.archlinux.org/packages/dantalian-git/)

Dependencies:

* [Python 3](http://www.python.org/)
* [GNU findutils](http://www.gnu.org/software/findutils/)
* [FUSE](http://fuse.sourceforge.net/) (Optional, for FUSE features)

Build dependencies:

* [setuptools](https://pypi.python.org/pypi/setuptools)
* [Sphinx](http://sphinx-doc.org/index.html)

Installation is simple.  Obtain the sources, then run:

    $ python setup.py install

This will most likely require root, and will install Dantalian globally
on the system.  Otherwise, you can use virtualenv, or install it for the
user:

    $ python setup.py install --user

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

Dantalian provides a script which can be invoked:

    $ dantalian <command>

Dantalian also installs a python package that can be imported by any
Python scripts:

    >>> import dantalian

Check the man pages for specifics:

    $ man 1 dantalian

If the man pages are not installed, they can be found in
reStructuredText form in `doc/man`.
