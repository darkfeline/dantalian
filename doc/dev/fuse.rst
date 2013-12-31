FUSE/Mounted Library Specification
==================================

The dantalian library API requires a :meth:`mount()` method, which uses
FUSE to mount a virtual file system representation of the library.

The mounted library provides a standard file-system-like interface to
libraries.  While the dantalian implementation of the library already
provides such an interface, other implementations may not by default.
Also, mounted libraries provide additional features even for dantalian's
existing file-system-like interface.

Virtual Spaces
--------------

In describing mounted library behavior, it is useful to divide the file
system space into a number of categories.

Directories corresponding to nodes are considered to be in virtual
space.  (Nodes are virtual space.)

Directories and files corresponding to real directories and files on the
file system are considered to be in real space.

There is also a subcategory for directories and files in real space:
real space files and directories pulled in by TagNodes are additionally
considered to be in tag space.  Note that this is not recursive.  Given
the following::

   TagNode/
      dir1/
         file1
      dir2/
      file2

TagNode is in virtual space as it is a node.  Everything under it is in
real space, but only ``dir1``, ``dir2``, and ``file2`` are in tag space.
``file1`` is not in tag space.

FUSE Operations
---------------

FUSE provides syscall-like operation hooks to emulate a file system.
Their implementations for mounted libraries are found as methods in the
:class:`dantalian.operations.TagOperations` class.

.. note::

   The behavior of the following operations on tag space is subject to
   change, due to planned additions to tag nodes.

.. method:: chmod(path, mode)
   :noindex:

   If `path` is in real or tag space, forward to OS.  If `path` is in
   virtual space, the operation is invalid and raises EINVAL.

.. method:: chown(path, uid, gid)
   :noindex:

   If `path` is in real or tag space, forward to OS.  If `path` is in
   virtual space, the operation is invalid and raises EINVAL.

.. method:: create(path, mode)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is also in tag
   space, tag the file accordingly. If `path` is in virtual space, the
   operation is invalid and raises EINVAL.

.. method:: getattr(path, fh=None)
   :noindex:

   If `path` is in real or tag space, forward to OS.  If `path` is in
   virtual space, get file attributes from the node.

.. method:: getxattr()
   :noindex:

   Not implemented.

.. method:: listxattr()
   :noindex:

   Not implemented.

.. method:: link(source, target)
   :noindex:

   .. note::

      Note that this is different from standard.  Usually link(a, b)
      creates a link at `b` to `a`, but this link(source, target)
      creates a link at `source` to `target`.  This is a quirk in the
      FUSE library used in dantalian.

   If `source` is in real space, link it (forward request to OS).  If
   `source` is also in tag space, tag the newly created link
   accordingly.  If `source` is in virtual space, raise EINVAL.

.. method:: mkdir(path, mode)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is also in tag
   space, additionally convert the new directory and tag it accordingly.
   If `path` is in virtual space, the operation is invalid and raises
   EINVAL.

.. method:: open(path, flags)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

.. method:: read(path, size, offset, fh)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

   .. note:

      `path` is ignored.  `fh` is used instead.

.. method:: readdir(path, fh)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, get information from the node.

.. method:: readlink(path)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

.. method:: removexattr()
   :noindex:

   Not implemented.

.. method:: rename(old, new)
   :noindex:

   This one is tricky; here's a handy chart.

   +------------+---------+-------------+-------------+
   | From To -> | Virtual | Tag         | Real        |
   +============+=========+=============+=============+
   | Virtual    | EINVAL  | EINVAL      | EINVAL      |
   +------------+---------+-------------+-------------+
   | Tag        | EINVAL  | untag, tag  | move, untag |
   +------------+---------+-------------+-------------+
   | Real       | EINVAL  | tag, remove | move        |
   +------------+---------+-------------+-------------+

.. method:: rmdir(path)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

.. method:: setxattr()
   :noindex:

   Not implemented.

.. method:: statfs(path)
   :noindex:

   Forward the request to the OS (via built-in os module).

.. method:: symlink(source, target)
   :noindex:

   .. note::

      This has the same quirk as `link()`.

   If `source` is in real space, link it (forward request to OS).  If
   `source` is also in tag space, tag the newly created symlink.  If
   `source` is in virtual space, raise EINVAL.

.. method:: truncate(path, length, fh=None)
   :noindex:

   If `path` is in real or tag space, forward to OS.  If `path` is in
   virtual space, the operation is invalid and raises EINVAL.

   .. note:

      `fh` is ignored.

.. method:: unlink(path)
   :noindex:

   If `source` is in real space, but not tag space, forward to OS.  If
   `source` is in tag space, untag the file instead.  If `source` is in
   virtual space, raise EINVAL.

.. method:: utimens(path, times=None)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

.. method:: write(path, data, offset, fh)
   :noindex:

   If `path` is in real space, forward to OS.  If `path` is in virtual
   space, the operation is invalid and raises EINVAL.

   .. note:

        `fh` is used; `path` is only used for verification.

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

Node File Attributes
--------------------

Nodes implement a basic set of default file attributes.

atime, ctime, mtime
   Defaults to time of node creation
uid, gid
   Defaults to process's uid and gid
mode
   Set directory bit, and permission bits 0o777 minus umask bits.
size
   Constant 4096

Currently these are dummy values and do not change, save for nlinks.

Socket Commands
---------------

Socket commands allow interaction with the mounted FUSE process, thereby
dynamically modifying parts of the virtual FUSE-mounted library.  Socket
commands may be invoked by the relevant commands of the dantalian CLI
script, or by ``echo``\ ing the commands directly into the FUSE library
socket.  The dantalian CLI script simply writes the commands to the
socket as well.

Currently, there are the following commands:

mknode path tag1 [tag2 ...]
   Make a TagNode at the given path with the given tags.  Make
   intermediary Nodes if needed.

rmnode path
   Remove the Node at the given path.
