Library
=======

Libraries are the fundamental level of abstraction in dantalian.  A library is 
an abstract tag-based file organization system layered transparently on top of
the underlying file system using hard links.  Libraries are created on
directories, which become the root for its library.  A special ``.dantalian``
directory is created in the root directory.

.. warning::
   I've said it before, but it bears repeating: dantalian uses hard links
   heavily.  Make sure you are familiar with how hard links work!  They are
   very powerful, but can be messy and/or dangerous if you are not familiar
   with them.  Especially take care not to accidently break hard links, e.g. by
   copying and removing files.  dantalian leverages the advantages hard links
   provide, but won't protect you from yourself!

Tags are directories, and all directories are potential tags (except
``.dantalian``, a special directory)  Files are "tagged" by creating a hard
link in the respective directory.  Files can have any number and combination of
tags.  File names and tag names are restricted only by the underlying file
system (so yes, Unicode and 50 character long names are all okay).  All files
of all types can be tagged, including symlinks.  dantalian provides
functionality such that even directories can be tagged, perfect for hardcore
file organizers.

Usage
-----

While it is possible to manage the library abstraction solely using standard
programs such as ``ln``, dantalian provides useful scripts for performing
operations such as tagging, untagging, and deleting, as commands for the
command-line script ``dantalian``.

See the manpage (linked here: :ref:`manpage`) for the commands for
``dantalian``.

Specific Requirements
---------------------

There are some requirements for libraries:

#) The root directory must be located on a POSIX filesystem that supports hard
   links (e.g., ``ext4``).
#) Everything under the root directory must be on one file system.
#) Do funky things with device mounts at your own risk.  This includes mounting
   another device inside a library, mounting a different library FUSE (more on
   this in :ref:`fuse`) in a library, and mounting the same library FUSE in
   itself.  Don't do it.

While the above may seem complicated, for most users, it should not be a
problem.  If you run into the above situations, chances are, you're an advanced
enough user to figure out why and how to fix them.

.. _name-conflicts:

Name conflicts
--------------

Files are hard linked under the tags that it possesses.  The file may have
different names in each of the directories, e.g. to avoid name conflicts.
dantalian provides "partial" support for files having different names.  The
library abstraction is completely sound in this case, but certain features may
not work, or may be less useful or harder to work with.  dantalian finds files
by the path to one of its hard links and manages them internally by hard link
references and inodes.

Currently, dantalian is unable to tag a file if a file with the same name
exists in that location (this feature will be implemented later).  However, you
can manually hard link the file with a different name and dantalian will work
perfectly.

Tagging Directories
-------------------

Because directories cannot be hard linked, dantalian must first convert them
before directories can be tagged.  Converting a directory moves it to a special
location under ``.dantalian`` and replaces it with an absolute symbolic link to
its new location.  Because converted directories are all kept in one location,
no two converted directories may have the same name.  However, the name of the
directory hitagiFS keeps track of and the name of the symbolic link that users
will be interacting with are separate.  Thus, if there's a naming conflict, the
actual directory can be renamed, and the symbolic links follow the naming rules
as above.  This feature imposes an extra requirement on the library root
directory.  Namely, when the root directory path is changed, the symbolic links
of all converted directories must be fixed.  dantalian provides this
functionality, but ``dantalian fix`` must be called each time.

Nested Libraries
----------------

Only one library can exist in any given directory, but libraries can be nested.
Behavior is well-defined, but I wouldn't recommend it unless you have a clear
use case and know what you are doing.  ``dantalian`` works with a single
library for its operations.  Usually, it will search up through the directories
and use the first library it finds, so take care of where you run it.  You can
also specify a specific library by using the ``--root`` option.

Scalability
-----------

dantalian's scalability ultimately depends on the host file system, but is
generally pretty lenient.  On ext4, for example, the main limiting factor is
number of files per directory, i.e., the number of files that have a given tag.
dantalian remains usable no matter the number, but if you have, say more than
10,000 files with a given tag, ``ls`` (specifically ``readdir()`` on the
kernel level) may begin to see performance issues.  However, file access is
unaffected.
