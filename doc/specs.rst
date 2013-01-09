******
Design
******

Specification
=============

HitagiFS mounts a root directory.  Every directory under it counts as a tag,
and files will appear under each directory it is tagged with.  Modifying one
will modify the rest, and deleting one will not affect the others.  hitagi will
support the following commands::

    tag
    utag
    find
    rm
    rename

Both files and tags (directories) can have multiple tags (parent directories).
Name collisions will not be automatically resolved.  By default, tagged
entities will retain the same name under different directories.

Implementation
==============

HitagiFS will be built on top of existing file system features, specifically
hard links and soft links.  hfs will support ``ext4`` primarily, but should
work for any similar file system.  HitagiFS will primarily use calls to
standard system utils.  As HitagiFS makes extensive use of hard links,
everything under its root must belong to one file system, that supports hard
links.

Tsun side
---------

Files will be handled with hard links, with a possible database cache to speed
up certain operations.

Dere side
---------

Because POSIX disallows directory hard links, directories will be handled with
soft links instead.  Tagged directories will reside in a special location in
the root directory, and will be symlinked to all other directories.  The name
of the directory will be kept the same when possible, and ask for a manual
rename when necessary.  Again, information will be cached in a database.

Example
=======
