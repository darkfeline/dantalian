dantalian-convert(1) -- Convert directories into taggable symbolic links
========================================================================

SYNOPSIS
--------

**dantalian** **convert** [*options*] *directory*...

DESCRIPTION
-----------

This command converts the given directories into symbolic links that can
be tagged.  The directories are moved to a special library directory,
and a symbolic link is created at its original path.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.
