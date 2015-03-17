dantalian-unload(1) -- Unload dtags
===================================

SYNOPSIS
--------

**dantalian** **unload** [*options*] *dir*

DESCRIPTION
-----------

Unload file system symlinks using a directory's dtags file.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.  If not
             specified, try to find a library automatically.
--all        Recursively unload for all directories.

SEE ALSO
--------

dantalian(1)
    Main man page
