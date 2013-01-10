******
Design
******

Specification
=============

hitagiFS operates on a root directory.  Every directory under it counts as a
tag, and files will appear under each directory it is tagged with.  Modifying
one will modify the rest, and deleting one will not affect the others.
hitagiFS will support the following commands:

tag
    Tag a file

untag
    Remove a tag from a file

find
    Find all files with the given tags

rm
    Remove a file globally

tags
    List tags of file

rename
    Rename a file globally or a single instance

convert
    Convert a directory to a symlink (so it's taggable)

init
    Create and initialize a hitagifs.

Both files and converted directories/tags can have multiple tags.  Unconverted
directories can only have one tag.  Name collisions will not be automatically
resolved.  By default, tagged entities will retain the same name under
different directories, but can be manually renamed individually.

Implementation
==============

hitagiFS will be built on top of existing file systems.  It relies heavily on
hard links, and supports any underlying (POSIX-compliant?) system that supports
hard links.  hitagiFS will primarily use calls to builtin Python library
:mod:`os` utils and standard system utils.  As hitagiFS makes extensive use of
hard links, everything under its root must belong to one file system.  As an
implementation detail, due to having to symlink directories, take care moving
the hitagiFS after creation.  Running ``hfs init`` on it after moving will
fix all of the symlinks (Running any command will fix it).  This may take some
time.

Tsun side
---------

Tagged files are hard linked under the respective directories.

Dere side
---------

Because POSIX disallows directory hard links, directories will be handled with
soft links instead.  Tagged directories will reside in a special location in
the root directory, and will be symlinked to all other directories.  The name
of the directory will be kept the same when possible, and ask for a manual
rename when necessary.

Thankfully, soft links *are* files, so can then be hard linked and tracked as
per Tsun implementation.
