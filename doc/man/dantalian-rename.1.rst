dantalian-rename(1) -- Rename tagged file
=========================================

SYNOPSIS
--------

**dantalian** **rename** [*options*] *file* *new*

DESCRIPTION
-----------

This command attempts to rename all hard links of the given file in the
library to the given name.  If this is not possible, it will append an
incrementing index to the end of the name, before the file extension,
until a free name is found, for each hard link.

OPTIONS
-------

**-h**, **--help**
    Print help information.

**--root**\=\ *path*
    Specify the root directory of the library to use.

EXAMPLES
--------

Rename all hard links to foo.txt, to bar.txt::

    $ dantalian rename foo.txt bar.txt

If the directory for one of the hard links already has a bar.txt,
**dantalian** will try to rename it bar.1.txt, then bar.2.txt, and so
on.
