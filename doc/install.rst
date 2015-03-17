Installation
============

Install using packages from your distribution if available.
Otherwise, see below for manual installation.

Arch Linux
----------

- `dantalian <https://aur.archlinux.org/packages/dantalian/>`_
- `dantalian-git <https://aur.archlinux.org/packages/dantalian-git/>`_

Manual installation
-------------------

Dependencies:

- `Python 3 <http://www.python.org/>`_

Build dependencies:

- `setuptools <https://pypi.python.org/pypi/setuptools>`_
- `Sphinx <http://sphinx-doc.org/index.html>`_ (for documentation)

Installation is simple.  Obtain the sources, then run::

    $ python setup.py install

This will most likely require root, and will install Dantalian globally
on the system.  Otherwise, you can use virtualenv, or install it for the
user::

    $ python setup.py install --user

It is recommended to install the man pages as well.  The man pages can
be built like so::

    $ cd doc
    $ make man

The man pages can be found in ``doc/_build/man``.  How they are installed
depends on your system.  On Arch Linux, man pages are installed in
``/usr/share/man`` as gzipped archives, so you would do the following::

    $ cd doc/_build/man
    $ gzip ./*
    # install ./* /usr/share/man/man1
