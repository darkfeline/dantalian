dantalian-find(1) -- Find files with tags
=========================================

SYNOPSIS
--------

**dantalian** **find** [*options*] *tag*...

DESCRIPTION
-----------

This command lists the files that have all of the given tags, using the
path corresponding to the first tag given.

For example, if *foo* has *tag1* and *tag2*, then

::

    $ dantalian find tag1 tag2

will print */path/to/tag1/foo*, while

::

    $ dantalian find tag2 tag1

will print */path/to/tag2/foo*.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.

--print0        Print the files separated with NULLs instead of
                newlines.
-t DESTINATION  Instead of printing the files, hard link them in the
                given destination directory, which may be provided as
                a path or a tag qualifier.  It may be outside of the
                library as well, but must be on the same file system.
