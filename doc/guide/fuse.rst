.. _fuse:

FUSE
====

dantalian offers an optional FUSE mount feature, which allows much more
powerful interaction with Libraries.

To use it, run ``dantalian mount /path/to/mount/location`` on the command line.
You will want to mount it somewhere outside of the library.

In addition to projecting the library into virtual FUSE space, you will also be
able to set up virtual tag groups, which represent the intersection of a set of
tags.  The two configuration files are ``.dantalian/mount`` and
``.dantalian/mount_custom``.  If the latter exists, it will be used; otherwise
the former is used.  The first configuration file is in JSON, and should look
as follows::

   [
       {"mount": "/path/to/mount/location",
        "tags": ["tag1", "tag2", "tag3"]},
       {"mount": "/path/to/another/mount",
        "tags": ["more", "tags"]}
   ]

Alternately, you may provide a custom script, ``mount_custom``.  It should be a
Python module that contains a function with the signature ``maketree(root)``.
It will be passed the root of the library.  You may write your own script to
set up a node tree and return it, and dantalian will handle the rest.  See
:meth:`dantalian.library._maketree` to see how dantalian creates a node tree
from the JSON for an example.

Nodes and virtual space
-----------------------

dantalian manages the virtual space using a node tree.

| FSNode
|   BorderNode
|     TagNode
|     RootNode

FSNodes simply represent virtual directories.  BorderNode is an abstract
subclass for nodes that lead back into real space (back to the underlying file
system).  There are two types: TagNodes project the intersection of their tags
under themselves, whereas the RootNode (there will only be one) projects the
library root under itself.

Functionally, it is useful to divide the virtual space into categories.  Paths
which point to nodes will be called nodespace.  Paths which point to files
directly under TagNodes are tagspace.  Paths which point more than one
directory beyond TagNodes or any files under RootNodes are outsidespace.

Name conflicts
--------------

Specified mounts (nodes) will obscure any files or directories with the same
name under RootNode.

File name conflicts for files under TagNodes will be resolved by adding the
inode number (which is guaranteed to be unique) at the end of the file name,
but before the extension.  E.g., if two files are both named ``file.mp3``, the
latter will appear as ``file.12345.mp3``, assuming its inode number is
``12345``.

FUSE Operations
---------------

FUSE intercepts calls to the kernel to perform file system operations, allowing
it to present a file system API in user space.  How it behaves depends on how
these operations are implemented.  See below for the implemented operations and
their behavior.  As a rule of thumb, interaction with nodespace is extremely
limited.  Calls to outsidespace will be passed on to the OS/underlying file
system.  Calls to tagspace will manipulate the tags on the files according to
the library paradigm.

.. autoclass:: dantalian.mount.TagOperations
