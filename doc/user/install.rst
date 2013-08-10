.. _install:

Installation
============

Simply install as you would any Python package: ``python setup.py
install``

Dependencies
------------

Required
^^^^^^^^

- Python 3
- GNU findutils.  This is something I debated over, but in order to find
  hard links, iteration is the only option.  While a database could be
  kept to keep track of hard links, changes not made through dantalian
  would then require rebuilding the database.  Thus, I decided to use
  findutils, as an optimized binary will run much faster than a
  recursive Python search.  (It also saves me from writing extra code.)

Optional
^^^^^^^^

- fuse.  There's a limit to what you can do with scripts alone, so
  dantalian also uses fuse to present additional features (See
  :ref:`fuse`).

Really Optional
^^^^^^^^^^^^^^^

- Sphinx, to build the documentation.  The documentation is built for
  each release, and it can be found online, so you shouldn't need this
  at all, but if for some reason you want/need to build it yourself, or
  you're using the latest development version, you'll need Sphinx to
  build the docs.
