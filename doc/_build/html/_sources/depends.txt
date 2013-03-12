Dependencies
============

- GNU findutils, specifically ``find``.  This is something I debated over.  In
  order to find hard links, iteration is the only option.  While a database
  could be kept to keep track of hard links, changes not made through dantalian
  would then require rebuilding the database, which doesn't help, as dantalian
  aims to be transparent.  Thus, we must walk the entire directory tree every
  time we want to do something, which is resource intensive.  Thus, I decided
  to use findutils, as an optimized binary will run much faster than a recursive
  Python search.  (It also saves me from writing extra code.)
- Sphinx, to build the documentation.  The documentation is built for each
  release, and it can be found online, so this is usually unnecessary, but if
  you want to build it yourself, or you're using the latest development
  version, you'll need Sphinx to build the docs.
- fuse, if you want to use FUSE mount features.
