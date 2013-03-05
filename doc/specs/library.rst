Library
=======

Libraries are the central data model in dantalian.  They project an alternate
tag-based file organization system transparently on top of the underlying file
system using hard links.

A library is created on a directory.  This directory becomes the root
directory for the library.  A special ``.dantalian`` directory is created in
the root directory.  The root directory must be located on a POSIX filesystem
that supports hard links (e.g., ``ext4``).  Everything under the root directory
must be on one file system.  Do funky things with device mounts at your own
risk.

Libraries use a conceptual abstraction of files and tags.  All directories
(except ``.dantalian``) under the root directory is a tag and is referred to
with its path relative to the root directory.  All files (not directories, but
including symbolic links) are files that can be tagged under the library
abstraction.

Files are hard linked under the tags that it possesses.  The file may have
different names in each of the directories, e.g. to avoid name conflicts.
dantalian provides "partial" support for files having different names.  The
library abstraction is completely sound in this case, but certain features may
not work, or may be less useful or harder to work with.  dantalian finds files
by the path to one of its hard links and manages them internally by hard link
references and inodes.  If you are using different names for a single file,
carefully read the documentation to see how hitagiFS handles paths in different
situations.

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
