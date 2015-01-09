Definitions
===========

General
-------

.. glossary::

   pathname
   path
      A string, consisting of filenames separated with forward slashes.

      - `/foo/bar/baz`
      - `foo/bar`

   basename
      The part of a path after the last forward slash in it.  If the path ends
      in a forward slash, then the basename is the empty string.

   dirname
      The part of a path before the last forward slash in it.

   filename
      A string, which in a directory maps to a link.  Cannot contain forward
      slashes.

      - `foo`
      - `.bar`

   link
      A directory entry pointing to a file.  A hard link.

   file
      A file in the file system, consisting of its inode and corresponding data
      blocks.  A file has at least one link pointing to it.

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

.. glossary::

   tagname
      A special type of pathname which begins with at least two forward
      slashes.  After stripping all forward slashes from the beginning of a
      tagname, the remaining string is considered a pathname relative to a
      given rootpath.

   rootpath
      A pathname that is used to resolve a tagname.

   library
      A directory which contains a link to a directory with the filename
      `.dantalian`.

A file is tagged with a directory if and only if there exists at least one hard
link to the file in that directory.

A file A is tagged at a path B if and only if B refers to a link that
points to A.

A directory may contain a link to a file with the filename `.dtags`.  The file
to which this link points contains tagnames which are each terminated with a
single newline.

A directory is internally tagged with a tagname if and only if its `.dtags`
file contains that tagname.

A directory A is externally tagged with a directory B if and only if there
exists at least one symlink in B that refers to A.

A directory A is externally tagged at pathname B if and only if B refers to a
symlink that refers to A.

Given a rootpath, a directory A being internally tagged with a tagname B is
equivalent to A being externally tagged at the pathname which is equivalent
to B.

Dantalian uses both internal and external tags, but internal tags are
considered more stable and reliable than external tags.
