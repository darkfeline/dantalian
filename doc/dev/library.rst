.. _library_abstract:

The Library Abstraction
=======================

Libraries are the fundamental level of abstraction in dantalian.  The
reference implementation is dantalian on an ext4 file system.  The
following is the specification for the library abstraction.

Library specification
---------------------

Libraries contain objects and tags.  Files are objects.  Tags are also
objects.  Objects can be tagged with any combination of tags.

Library on a file system
------------------------

A library is a given directory and all subdirectories.  The given
directory is the root directory of the library.  All subdirectories are
tags.  The root directory is a tag.  Tags are the absolute path of the
respective directory relative to the root directory (e.g., the tag ``/``
is the root directory, and the tag ``/tag`` is the directory named
``tag`` in the root directory).  All subdirectories and all files
contained in the root directory and subdirectories are objects.

.. note::

   The root directory is not an object.

An object is tagged if it appears within the corresponding directory.
Every object can be tagged with any combination of tags.  A file can
appear within a directory multiple times; such a file will be considered
as tagged once with the corresponding tag.  A directory can be tagged
with its own corresponding tag.

.. note::
   Directories can only be tagged once by virtue of common file system
   limitations.  Symbolic links act identically to files.  In order to
   tag a directory multiple times, the directory must be converted
   (stored in a designated location and replaced with a corresponding
   symbolic link).  If a file system supports directory hard links, this
   reference abstraction still holds.

.. note::
   Due to practical reasons, the directory ``.dantalian`` in the root
   directory is reserved for internal use.  It is not considered a valid
   tag or object.
