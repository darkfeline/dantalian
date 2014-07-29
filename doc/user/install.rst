Installation
============

Dependencies
------------

* `Python 3 <http://www.python.org/>`_
* `GNU findutils <http://www.gnu.org/software/findutils/>`_
* `FUSE <http://fuse.sourceforge.net/>`_ (Optional, for FUSE features)

Build dependencies:

* `setuptools <https://pypi.python.org/pypi/setuptools>`_
* `Sphinx <http://sphinx-doc.org/index.html>`_

Using packages
--------------

The easiest method of installation is via packages.  However, Dantalian
currently only has packages for Arch Linux.

If there are no packages available for your distribution, you will need
to install Dantalian manually.  If you are able, please consider making
a package yourself (Refer to the :doc:`/dev` for information on
packaging Dantalian).

* `Arch Linux (AUR) <https://aur.archlinux.org/packages/dantalian/>`_
* `Arch Linux (AUR) (git) <https://aur.archlinux.org/packages/dantalian-git/>`_

Manual Installation
-------------------

Make sure you have satisfied all of the dependencies above.  Dantalian
is installed just like any Python package::

    $ python setup.py install

This will most likely require root, and will install Dantalian globally
on the system.  Otherwise, you can use virtualenv, or install it for the
user::

    $ python setup.py install --user

It is recommended to install the man pages as well.  The man pages can
be built like so::

    $ cd doc
    $ make man

The man pages can be found in :file:`doc/_build/man`.  How they are
installed depends on your system.  On Arch Linux, man pages are
installed in :file:`/usr/share/man` as gzipped archives, so you would do
the following::

    $ cd doc/_build/man
    $ gzip ./*
    # install ./* /usr/share/man/man1
