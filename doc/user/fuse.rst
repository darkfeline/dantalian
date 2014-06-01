.. _fuse:

FUSE Usage
==========

Dantalian offers an optional FUSE mount feature, which allows much more
powerful interaction with libraries.

To use it, run ``dantalian mount /path/to/mount/location`` on the
command line.  You will want to mount it somewhere outside of the
library.

Usage
-----

For the most part, FUSE-mounted libraries behave exactly like regular
libraries, so you can use the regular Dantalian commands as well as
regular file system operations to interact with it.  However, certain
Dantalian commands behave differently or are restricted for sanity's
sake (for example, you cannot ``mount`` a FUSE-mounted library, for
obvious reasons).  Dantalian distinguishes between a mounted library and
a regular library by the existence of a virtual directory
``.dantalian-fuse``, which simply points to ``.dantalian``.

To unmount, use ``fusermount -u path/to/mount``.

See :ref:`names` for information about name resolution.

Nodes and virtual space
-----------------------

Dantalian manages the virtual space using a node tree.

Node types:

* FSNode

  * BorderNode

    * TagNode
    * RootNode

FSNodes represent virtual directories.  BorderNode is an abstract
subclass for nodes that lead back into real space (back to the
underlying file system).  There are two types: TagNodes project the
intersection of their tags under themselves, whereas the RootNode (there
will only be one, at the root) projects the library root under itself.

It is useful to divide the virtual space into categories when describing
Dantalian FUSE behavior.  Paths which point to nodes are in nodespace.
Paths which point to files directly under TagNodes are in tagspace.
Paths which point more than one directory beyond TagNodes or any files
under RootNodes are in outsidespace.

Socket Operations
-----------------

You can also interact directly with a FUSE-mounted library using socket
operations.  FUSE-mounted libraries open a socket at
``.dantalian/fuse.sock``.  Dantalian provides scripts that allow you to
interact dynamically with a mounted library, but they simply echo
standard commands to the socket, which can be done by hand (like all
other Dantalian operations) from, e.g. a remote client that doesn't have
Dantalian installed.  For example, the socket command::

   $ dantalian mknode path/to/node tag1 tag2

can be done by::

   $ echo mknode path/to/node tag1 tag2 > library/.dantalian/fuse.sock

The socket processes commands much like a shell, so make sure to quote
anything that contains spaces.

A list of socket commands can be found in the :ref:`commands`.

FUSE Operations
---------------

FUSE intercepts calls to the kernel to perform file system operations,
allowing it to present a file system API in user space.  How it behaves
depends on how these operations are implemented.  As a rule of thumb,
interaction with nodespace is extremely limited.  Calls to outsidespace
will be passed on to the OS/underlying file system.  Calls to tagspace
will manipulate the tags on the files according to the library rules.

These operations are only documented in the source code currently.
