Specification
=============

hitagiFS
--------

A hitagiFS is created on a directory.  This directory becomes the root
directory for the hitagifs.  A special ``.hitagifs`` directory is created in
the root directory.  The root directory must be located on a POSIX filesystem
that supports hard links (e.g., ``ext4``).  Everything under the root directory
must be on one file system.

hitagiFS uses a conceptual abstraction of files and tags.  All directories
(except ``.hitagifs``) under the root directory is a tag and is referred to
with its path relative to the root directory.  All files (not directories, but
including symbolic links) are files that can be tagged under the hitagiFS
abstraction.

Files are hard linked under the tags that it possesses.  The file may have
different names in each of the directories, e.g. to avoid name conflicts.
hitagiFS provides "partial" support for files having different names.  The
hitagiFS abstraction is completely sound in this case, but certain features may
not work, or may be less useful or harder to work with.  hitagiFS finds files
by the path to one of its hard links and manages them internally by hard link
references and inodes.  If you are using different names for a single file,
carefully read the documentation to see how hitagiFS handles paths in different
situations.

Because directories cannot be hard linked, hitagiFS must first convert them
before directories can be tagged.  Converting a directory moves it to a special
location under ``.hitagifs`` and replaces it with an absolute symbolic link to
its new location.  Because converted directories are all kept in one location,
no converted directory may have the same name.  However, the name of the
directory hitagiFS keeps track of and the name of the symbolic link that users
will be interacting with are separate.  Thus, if there's a naming conflict, the
actual directory can be renamed, and the symbolic links follow the naming rules
as above.  This feature imposes an extra requirement on the hitagiFS root
directory.  When the root directory path is changed, the symbolic links of all
converted directories must be fixed.  hitagiFS provides this functionality.

FUSE Mount
----------

hitagiFS offers a FUSE mounts feature.  Currently, this allows you to "mount"
a FUSE file system that contains files with certain combinations of tags.  The
configuration file for FUSE is at ``.hitagifs/mount``.  The FUSE file system
will be mounted under ``fuse`` under the root directory.  The configuration
file is in JSON, and should look as follows::

   [
       {"mount": "/path/to/mount/location",
        "tags": ["tag1", "tag2", "tag3"]},
       {"mount": "/path/to/another/mount",
        "tags": ["more", "tags"]}
   ]

With the above configuration file, after mounting, the following directory tree
will be found at the mount location::

   /
   /path
   /path/to
   /path/to/mount
   /path/to/mount/location
   /path/to/another
   /path/to/another/mount

Only the actual mounts (``/path/to/mount/location`` and
``/path/to/another/mount``) can be interacted with in any significant way.  The
intermediate paths (``/path``, ``/path/to`` and so on) are completely virtual
and generally cannot be interacted with in meaningful ways beyond navigating to
other virtual directories.  The mounts will display the intersection of the
given tags (all files with all of the tags).  For example, ``ls location`` will
list all files who have the ``tag1``, ``tag2``, and ``tag3`` tags.  The file
name a given file will be displayed under is calculated in the following order.

   #. The file name that the file has under the first tag given in the ``tags``
      list, unless it conflicts with the name of a previously found file.
   #. An index will be added to the end of the file, but before a file
      extension.  The index is incremented until it doesn't conflict with a
      previously found file.

For example, a file which is tagged ``tag1/file1``, ``tag2/file2``, and
``tag3/file2`` and using the above example configuration, would be called
``file1`` under ``location``, and in order as the name conflicts, ``file1.1``,
``file1.2`` and so on.  A file with an extension, e.g. ``file.mp3``, will be
renamed ``file.1.mp3``, ``file.2.mp3``, and so on.

FUSE Operations
^^^^^^^^^^^^^^^

FUSE intercepts calls to the kernel to perform file system operations, allowing
it to present a file system API in user space.  How it behaves depends on how
these operations are implemented.  As a rule of thumb, most operations
performed beyond the designated mount points are forwarded to the underlying
file system and are not permitted on the virtual directories before the
designated mount points.
