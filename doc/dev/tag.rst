Tags
====

Tags can be specified as absolute or relative.

Absolute tags start with ``/``, like absolute paths.  They describe a
tag/directory relative to the library root.

Absolute tags must be in standard POSIX path format, e.g. ``/`` is the
delimiter, and is illegal in names, but all other characters are valid
in part names.

Relative tags do not start with ``/``.  They describe a tag/directory
relative to the current working directory.  Directories not under the
library root are not valid tags for that library.

Relative tags may be in the format of the host operating system or file
system.
