.. _library_abstract:

The Library Abstraction
=======================

Libraries are the fundamental level of abstraction in dantalian.  The
reference implementation is dantalian on an ext4 file system.

Library specification
---------------------

Libraries contain objects and tags.  Files are objects.  Tags are also
objects.  Objects can be tagged with any combination of tags.

Library on a file system
------------------------

A library is a given directory and all subdirectories.  The given
directory is the root directory of the library.  All subdirectories are
tags.  All subdirectories and all files contained in the root directory
and subdirectories are objects.

An object is tagged if it appears within the corresponding directory.
Every object can be tagged with any combination of tags.  A file can
appear within a directory multiple times; it will be considered as
tagged once with the corresponding tag.  A directory can be tagged with
its own corresponding tag.

.. note::
   Directories can only be tagged once by virtue of common file system
   limitations.  Symbolic links act identically to files.  If a file
   system supports directory hard links, this reference abstraction
   still holds.

.. note::
   Due to practical reasons, the directory ``.dantalian`` in the root
   directory is reserved for internal use.  It is not considered a valid
   tag or object.
