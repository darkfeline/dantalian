FUSE/Mounted Library Specification
==================================

The Library API requires a :meth:`mount()` method, which uses FUSE to
mount a virtual file system representation of the library.

The mounted library provides a standard file-system-like interface to
libraries.  While the dantalian implementation of the library already
provides such an interface, other implementations may not by default.
Also, mounted libraries provide additional features even for dantalian's
existing file-system-like interface.

Virtual Spaces
--------------

In describing mounted library behavior, it is useful to divide the file
system space into three categories.

FUSE Operations
---------------

FUSE provides syscall-like operation hooks to emulate a file system.
Their implementations for mounted libraries are found as methods in the
:class:`dantalian.operations.TagOperations` class.

.. method:: chmod(path, mode)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: chown(path, uid, gid)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: create(path, mode)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is tagged,
   additionally add its tags.  If `path` is a node, the operation is
   invalid and raises EINVAL.

.. method:: getattr(path, fh=None)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   get attributes from node.

.. method:: getxattr()
   :noindex:

   Not implemented.

.. method:: listxattr()
   :noindex:

   Not implemented.

.. method:: link(source, target)
   :noindex:

   Note that this is different from standard.  Usually link(a, b)
   creates a link at a to b, but this link(source, target) creates a
   link at source to target.

   If `source` is tagged, tag it.  If `source` is outside, link it.  If
   `source` is a node, raise EINVAL

.. method:: mkdir(path, mode)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If it is tagged,
   additionally convert it and add tags.  If `path` is a node, the
   operation is invalid and raises EINVAL.

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

   If `path` points beyond a node, forward the request to the OS (via
   built-in os module).  Once a directory is created, it is converted
   and tagged with all of the tags of the furthest node.  Otherwise the
   operation is invalid and raises EINVAL.

.. method:: open(path, flags)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: read(path, size, offset, fh)
   :noindex:

   `path` is ignored.  Forward the request to the OS (via built-in os
   module) with the file descriptor.

.. method:: readdir(path, fh)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   a directory listing containing '.' and '..' is made and generated
   entries from the node's __iter__ are added.

.. method:: readlink(path)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: removexattr()
   :noindex:

   Not implemented.

.. method:: rename(old, new)
   :noindex:

   This one is tricky; here's a handy chart.

   +---------+---------+-------------------+-------------------+
   | Old     | To Node | To Tagged         | To Outside        |
   +=========+=========+===================+===================+
   | Node    | EINVAL  | EINVAL            | EINVAL            |
   +---------+---------+-------------------+-------------------+
   | Tagged  | EINVAL  | untag, tag        | move, untag       |
   +---------+---------+-------------------+-------------------+
   | Outside | EINVAL  | tag, remove       | move              |
   +---------+---------+-------------------+-------------------+

.. method:: rmdir(path)
   :noindex:

   If `path` is outside or tagged, forward to OS.  (If it's tagged, it's
   not a dir, but we'll let the OS handle that =))  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: setxattr()
   :noindex:

   Not implemented.

.. method:: statfs(path)
   :noindex:

   Forward the request to the OS (via built-in os module).

.. method:: symlink(source, target)
   :noindex:

   Note that this is different from standard.  Usually link(a, b)
   creates a link at a to b, but this link(source, target) creates a
   link at source to target.

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: truncate(path, length, fh=None)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If it is tagged,
   additionally add its tags.  If `path` is a node, the operation is
   invalid and raises EINVAL. `fh` is ignored.

.. method:: unlink(path)
   :noindex:

   If `path` is tagged, untag.  If `path` is outside, forward to OS.  If
   `path` is a node, the operation is invalid and raises EINVAL.

.. method:: utimens(path, times=None)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.

.. method:: write(path, data, offset, fh)
   :noindex:

   If `path` is outside or tagged, forward to OS.  If `path` is a node,
   the operation is invalid and raises EINVAL.  `fh` is used; `path` is
   only used for verification.

Nodes
-----

Nodes are used to construct and maintain the virtual library file
system.  Internally, nodes are implemented as mapping type data objects.

Currently, there are three node types and one virtual node class.

:class:`dantalian.tree.BaseNode` is the fundamental node class,
representing a virtual directory in a mounted library.  Its
implementation is :class:`dantalian.tree.Node`.

:class:`dantalian.tree.BorderNode` is a virtual class/interface for
nodes that pull the host file system into the virtual space (i.e.,
tagged files)

It has two subclasses, :class:`dantalian.tree.BaseRootNode` and
:class:`dantalian.tree.BaseTagNode`, and their implementations
:class:`dantalian.tree.RootNode` and :class:`dantalian.tree.TagNode`,
respectively.

RootNodes pull all of the tags in the library under themselves as
virtual directories.  They will usually be the root node for the node
trees that describe the mounted library structure, but this is not
necessary.

TagNodes pull the intersection set of files of a given set of tags under
themselves.
