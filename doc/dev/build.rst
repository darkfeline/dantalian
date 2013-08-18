Building
========

Source Package
--------------

Refer to :ref:`depend` for the build dependencies.

I recommend that you use a Python virtualenv for building dantalian.

Get a copy of the code from the repository of the version or commit you
are building::

   $ git clone https://github.com/darkfeline/dantalian.git
   # Use development branch?
   $ git checkout develop

Install dantalian (needed for building the documentation)::

   $ python setup.py install

Build the documentation::

   $ cd doc
   $ make html
   $ make man

Make the source package::

   $ cd ..
   $ python setup.py sdist

Packages will be in the ``dist`` directory.

Built Package
-------------

Built packages can also be made for distribution, e.g., for a
package repository.  Likely, this will entail
repository/system/architecture/package-manager-specific configuration.

A simple vanilla package can be built by creating a ``setup.cfg`` with
the following text::

   [install]
   prefix=/usr

and running::

   $ python setup.py bdist
