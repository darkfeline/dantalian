Installation
============

Packages
--------

The easiest and recommended method of installation is via packages
provided by your distribution.

- Arch Linux (AUR): https://aur.archlinux.org/packages/dantalian/

If there are no packages available for your distribution, you will need
to install Dantalian manually.

Manual Installation
-------------------

Dependencies
^^^^^^^^^^^^

Dantalian requires `Python 3`_ and GNU findutils_.  Dantalian optionally
requires FUSE_, however, FUSE is needed for many features and you should
install it unless you know you do not need it.

.. _Python 3: http://www.python.org/
.. _findutils: http://www.gnu.org/software/findutils/
.. _FUSE: http://fuse.sourceforge.net/

Installation
^^^^^^^^^^^^

Dantalian uses Python's built-in ``distutils`` package and can be
installed similarly as any Python package::

   $ python setup.py install

This will most likely require root, and will install Dantalian globally.
You can use virtualenv, or install it for the user::

   $ python setup.py install --user
