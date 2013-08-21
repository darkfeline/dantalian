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
