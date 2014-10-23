dantalian-fix(1) -- Fix symbolic links of converted directories
===============================================================

SYNOPSIS
--------

**dantalian** **fix** [*options*]

DESCRIPTION
-----------

This command fixes the symbolic links of converted directories after the
library has been moved or otherwise has its path changed.  Hard link
relationships of the symbolic links are preserved *only in the library*.
(This is because Linux system calls do not allow for editing symbolic
links in place. They must be unlinked and remade.)  Symbolic links are
removed and a new symbolic link is made then relinked.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.
