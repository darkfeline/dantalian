.. TODO merge this with user/basic.  Also, some of this info is
.. deprecated by hard links guide.

Libraries
=========

A library is an abstract tag-based file organization system layered
transparently on top of the underlying file system using hard links.
Libraries are created on directories, which become the root for its
library.  A special :file:`.dantalian` directory is created in the
root directory of a library.

.. note::

    Dantalian uses hard links heavily.  Make sure you are familiar
    with how hard links work!  They are very powerful, but can be
    messy and/or dangerous if you are not familiar with them.
    Especially take care not to accidently break hard links, e.g., by
    copying and removing files.  Dantalian leverages the advantages
    hard links provide, but won't protect you from yourself!

Tags are directories, and all directories are potential tags
(including :file:`.dantalian`, however you shouldn't use it as such).
Files are "tagged" by creating a hard link in the respective
directory.  Files can have any number and combination of tags.  File
names and tag names are restricted only by the underlying file system
(on ``ext4``, for example, up to 255 bytes and all characters except
``/`` are allowed, so knock yourself out).  All files of all types can
be tagged, including symlinks.  Dantalian provides functionality such
that even directories can be tagged, perfect for hardcore file
organizers.

Usage
-----

While it is possible to manage the library solely using standard
utilities such as :command:`ln`, :command:`mv`, etc., Dantalian
provides useful scripts for performing operations, such as tagging,
untagging, and deleting.

Check the man pages for the command reference.

Specific Requirements
---------------------

There are some requirements for libraries:

#) The root directory must be located on a POSIX filesystem that
   supports hard links (e.g., ``ext4``).
#) Everything under the root directory must be on one contiguous file
   system.
#) Do funky things with block device mounts at your own risk.  This
   includes mounting another device inside a library, mounting a
   different library FUSE (more on this in :ref:`fuse`) in a library,
   and mounting the same library FUSE in itself.

While the above may seem complicated, for most users, it should not be
a problem.  If you run into the above situations, chances are, you're
an advanced enough user to figure out why and how to fix them.

.. _name_conflicts:

Name Conflicts
--------------

Files are hard linked under the tags that it possesses.  The file may
have different names in each of the directories, e.g., to avoid name
conflicts.  Dantalian works fine in this case, although it may be
confusing for you, the human user, because Dantalian finds files by the
path to one of its hard links and manages them internally by hard link
references and inodes.

Dantalian will resolve name conflicts if it needs to, e.g., to create a
hard link to tag a file.  See :ref:`names` for more information on
name conflict resolution.

Tagging Directories
-------------------

Directories generally are not allowed to be hard linked in most file
systems, for various reasons.  However, symbolic links are regular
files and thus can be hard linked, even if they point to a directory.
Dantalian uses this to implement tagging of directories.

Dantalian can convert directories.  Converting a directory moves it to
a special location under ``.dantalian`` and replaces it with an
absolute symbolic link to its new location.  This allows directories
to be tagged just like other files.  In other words, Dantalian will
manage the actual directory, and a symbolic link will be used in place
of it for tagging.

This feature imposes an extra requirement on the library root
directory.  Namely, when the root directory path is changed, the
symbolic links of all converted directories must be fixed by running
``dantalian fix``.  Also, unlike regular files, which can be freely
hard linked to directories outside of the library (and tagged in other
libraries), if you hard link the symbolic link of a
dantalian-converted directory outside of it, move the library, and run
``dantalian fix``, it will break the external hard links.  If this is
one of your use cases, place the directories in a fixed location
outside of the library, create a symbolic link manually, and then tag
it with Dantalian instead of using ``dantalian convert``.

Because converted directories are all kept in one location, no two
converted directories may have the same name.  However, the name of
the directory Dantalian keeps track of and the name of the symbolic
link that the user interacts with are independent of eac hoterh.
Thus, if there's a naming conflict, the actual directory can be
renamed, and the symbolic links follow the naming rules as above.

Moving Libraries
----------------

Since libraries are simply directories, moving and/or backing up
libraries is very simple.  There are two thing to keep in mind:  use
``rsync -H`` to preserve hard links, and don't forget to run
``dantalian fix`` to fix absolute symbolic links for converted
directories.  The latter is important as Dantalian currently will
*not* check if it needs fixing.

Nested Libraries
----------------

Only one library can exist in any given directory, but libraries can
be nested.  Behavior is well-defined, but I wouldn't recommend it
unless you have a clear use case and know what you are doing.
Dantalian works with a single library for its operations.  Usually, it
will search up through the directories and use the first library it
finds, so take care where you run it.  You can also specify a specific
library by using the ``--root`` option.  In fact, if you are nesting
libraries, it is recommended to *always* use ``--root``.

Scalability
-----------

Dantalian's scalability ultimately depends on the host file system,
but it is generally pretty lenient.  On ``ext4``, for example, the
main limiting factor is number of files per directory, i.e., the
number of files that have a given tag.  Dantalian remains usable no
matter the number, but if you have, say, more than 10,000 files with a
given tag, ``ls`` (specifically ``readdir()`` on the kernel level) may
begin to see performance issues.  However, file access will not be
affected.

Note that you can use LVM_ to create virtual partitions that span
multiple physical drives, if necessary.

.. _LVM: https://wiki.archlinux.org/index.php/LVM

Rough performance numbers
-------------------------

Space
    Depends, ~20-200B per tag per file

Time
    Constant for file access, linear for enumerating files of a tag.
    (This is pretty straightforward; the only thing is that a
    directory lookup in, e.g., a file manager, might lock up while it
    is :command:`ls`\ ing a directory
