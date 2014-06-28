dantalian-find(1) -- Find files with tags
=========================================

SYNOPSIS
--------

**dantalian** **find** [*options*] *tag*...

DESCRIPTION
-----------

This command lists the files that have all of the given tags.

OPTIONS
-------

**-h**, **--help**
    Print help information.

**--root**\=\ *path*
    Specify the root directory of the library to use.

**--print0**
    Print the files separated with NULLs instead of newlines.

**-t**\=\ *destination*
    Instead of printing the files, hard link them in the given
    destination directory, which may be provided as a path or a tag
    qualifier.  It may be outside of the library as well, but must be on
    the same file system.
