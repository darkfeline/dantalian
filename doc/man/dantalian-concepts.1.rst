dantalian-concepts(1) -- Concepts and general information
=========================================================

TAGS AND HARD LINKS
-------------------

Directories are tags, and tags are directories.  A file is considered
tagged with a given tag if it has at least one hard link in the
respective directory.  The name of the hard link does not matter, and
there can be more than one hard link for a file in a given directory.

Tags can be referred to interchangeably using the path to their
respective directory, either relative or absolute, or by their tag
qualifier (unless otherwise noted).  Tag qualifiers are similar to UNIX
paths, but are relative to their library's root directory and are
preceded with two slashes.

For example, if the root of the library is ``/home/user/library``, and
the library contains a directory ``/home/user/library/foo/bar``, the tag
qualifier for that directory would be ``//foo/bar``.
