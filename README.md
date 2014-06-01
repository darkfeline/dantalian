# Dantalian README

Project Website: <http://darkfeline.github.io/dantalian/>

Dantalian is a multi-dimensionally hierarchical tag-based file
organization system, implemented using hard links.

Comprehensive documentation can be found online at
<http://dantalian.readthedocs.org/en/>

## Dependencies

Dantalian is written in [Python 3][1], and additionally requires [GNU
findutils][2] and [FUSE][3] for important features.

[1]: http://www.python.org/
[2]: http://fuse.sourceforge.net/
[3]: https://www.gnu.org/software/findutils/

Dantalian works on contiguous POSIX-compatible file systems.  Specific
requirements may vary.

## Installation

Dantalian can be installed like all Python packages:

    $ python setup.py install

This will install Dantalian globally, which may or may not be preferred
and will probably require root.  Alternatively:

    $ python setup.py install --user

will install Dantalian locally for the current user.

## Usage

Dantalian provides a script which can be invoked:

    $ dantalian <command>

Dantalian also installs a python package that can be imported by any
Python scripts:

    >>> import dantalian

See the manpage and the documentation for more information.
