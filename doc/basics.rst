Definitions
===========

General
-------

.. glossary::

   pathname
      A path.

      - `/foo/bar/baz`
      - `foo/bar`

   filename
      A key in a directory which maps to a link.  Cannot contain forward slashes.

      - `foo`
      - `.bar`

   link
      A directory entry pointing to a file.  A hard link.

   file
      A file in the file system, consisting of its inode and
      corresponding data blocks.  A file has at least one link pointing to it.

   directory
      A special type of file, which maps filenames to links.

   symbolic link
   symlink
      A special type of link, which contains a string instead of pointing to a
      file.  The string is used as a pathname.

A pathname consists of filenames separated with forward slashes.  A filename
refers to a link in a directory.  A link points to a file.  A file has at least
one link pointing to it.  A directory is a special file which can only have one
link pointing to it and maps filenames to links.

Dantalian-specific
------------------

Dantalian definitions:

A file is tagged with a directory if and only if there exists at least one hard
link to the file in that directory.
