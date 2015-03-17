.. _tagging:

Tagging
=======

.. module:: dantalian.tagging

Dantalian provides a simple implementation of tagging with hard links using the
module :mod:`dantalian.tagging`.  Tagging works thusly:

Objects can be arbitrarily tagged with tags.  Objects can be both files and
directories, and tags can only be directories.  An object is tagged with a
given tag when it has a link in the corresponding directory.  Similarly, an
object is untagged by removing all of its links in the corresponding directory.

.. function:: tag(rootpath, path, directory)

   Tag a file (or directory) with a directory.  In effect, this tries to link
   `path` inside `directory` using :func:`dantalian.base.link`.  It will try to
   use the same :term:`basename` as the given file if possible; if not, it will
   try to find a similar name that is free.

.. function:: untag(rootpath, path, directory)

   Untag a file (or directory) from a directory.  Essentially calls
   :func:`dantalian.base.unlink` on all links of the target file in the given
   directory.
   
