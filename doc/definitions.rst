Definitions
===========

This section contains definitions of terms used in the documentation.

General
-------

The following are general terms you should be familiar with, but are provided
here for clarification and refernce.

.. glossary::

   pathname
   path
      A string, consisting of filenames separated with forward slashes.

   basename
      The part of a path after the last forward slash in it.  If the path ends
      in a forward slash, then the basename is the empty string.

   dirname
      The part of a path before the last forward slash in it.

   filename
      A string, which in a directory maps to a link.  Cannot contain forward
      slashes.  Filenames are components of paths.

   hard link
   link
      A directory entry pointing to a file.

   file
      A file in the file system, consisting of its inode and corresponding data
      blocks.  A file has at least one link pointing to it.

   directory
      A special type of file, which maps filenames to links and can only have
      one link referring to it.

   symbolic link
   symlink
      A special type of link, which contains a string instead of pointing to a
      file.  The string is used as a pathname.

Dantalian-specific
------------------

The following are terms that are used by Dantalian internally and in this
documentation.

.. glossary::

   tagname
      A special type of pathname which begins with at least two forward
      slashes.  After stripping all forward slashes from the beginning of a
      tagname, the remaining string is considered a pathname relative to a
      given rootpath.  See :ref:`tagnames`.

   rootpath
      A pathname that is used to resolve a tagname.  See :ref:`tagnames`.

   library
      A directory which contains a link to a directory with the filename
      `.dantalian`.  See :ref:`libraries`.
