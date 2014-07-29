dantalian-rm(1) -- Remove all tags of files
===========================================

SYNOPSIS
--------

**dantalian** **rm** [*options*] *file*...

DESCRIPTION
-----------

This command removes all of the tags of the given files.  In most cases,
this is the same as deleting the file entirely, unless there are hard
links to the files outside of the library.  Hard links to the files that
reside outside of the library are not affected.

OPTIONS
-------

**-h**, **--help**
    Print help information.

**--root**\=\ *path*
    Specify the root directory of the library to use.
