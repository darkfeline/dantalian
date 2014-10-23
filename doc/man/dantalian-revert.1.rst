dantalian-revert(1) -- Revert converted directories from symbolic links
=======================================================================

SYNOPSIS
--------

**dantalian** **revert** [*options*] *file*...

DESCRIPTION
-----------

This command reverts converted directories back into directories from
symbolic links.  The directories must only have one tag (alternatively,
one hard link) in the library.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.
