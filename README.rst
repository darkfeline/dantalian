dantalian README
================

Project Website: http://darkfeline.github.io/dantalian/

dantalian is a multi-dimensionally hierarchical tag-based file
organization system, implemented using hard links.

More in depth documentation may be found in this distribution, if it had
been built or included, or online at
http://dantalian.readthedocs.org/en/

Installation
------------

dantalian can be installed like all Python packages::

  $ python setup.py install

This will install dantalian globally, which may or may not be preferred
and will probably require root.  Alternatively::

  $ python setup.py install --user

will install dantalian locally for the current user.

Usage
-----

dantalian provides a script which can be invoked::

  $ dantalian <command>

dantalian also installs a python package that can be imported by any
Python scripts::

  >>> import dantalian

See the manpage and the documentation for more information
