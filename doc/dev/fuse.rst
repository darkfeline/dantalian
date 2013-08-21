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
