Library Operations
==================

dantalian describes and implements various tiers of operations described
below.  See :ref:`library_abstract` for a reference to the library
abstraction specification.

BaseLibrary
-----------

BaseLibrary is the fundamental abstract library class.  It requires the
following methods and invariants:

tag(file, tag)
   `file` should be tagged with `tag` after call, regardless of whether
   it was before.

untag(file, tag)
   `file` should not be tagged with `tag` after call, regardless of
   whether it was before.

listtags(file)
   Return a list of all of the tags of `file`.

find(tags)
   Return a list of files that have all of the given tags in `tags`.

mount(path, tree)
   Mount a virtual representation of the library representation `tree`
   at `path`.  This may be left unimplemented or with a dummy
   implementation.

BaseLibrary exists to facilitate alternate implementations of dantalian
libraries not based on file systems, e.g., a MySQL backend.

BaseFSLibrary
-------------

BaseFSLibrary is the abstract class for libraries implemented on a file
system.  It requires the following methods and invariants in addition to
those described in BaseLibrary:

tag(file, tag)
   If `file` does not have a hard link under the `tag` directory, make
   one.  `file` has at least one hard link under the `tag` directory
   after call.

untag(file, tag)
   `file` has no hard links under the `tag` directory after call,
   regardless of whether it did before.

Library
-------

Library is the actual implementation that dantalian provides.  It
implements the following public methods and invariants in addition to
those described in BaseFSLibrary (Filename/path conflicts will be
resolved according to :ref:`rename_alg`.):

tag(file, tag)
   Tag file as in BaseFSLibrary.  Resolve name conflict if necessary.

untag(file, tag)
   Same as BaseFSLibrary

listtags(file)
   Same as BaseFSLibrary

convert(dir)
   Store directory `dir` internally and replace the original with a
   symbolic link with the same name pointing to the absolute path of the
   stored directory.  Resolve name conflict if necessary (if a file with
   the same name is made in between moving the directory and creating
   the symbolic link, for example).

cleandirs()
   Remove all directories stored internally that no longer have any
   symbolic links referring to them in the library.

find(tags)
   Same as BaseFSLibrary

rm(file)
   Remove all hard links to `file` in the library.  Any errors will be
   reported and removal will resume for remaining hard links.

rename(file, new)
   Rename all hard links to `file` in the library to `new`.  File name
   conflicts are resolved and reported.  Any errors
   will be reported and renaming will resume for remaining hard links.

fix()
   Fix the absolute paths of symbolic links in the library to internally
   stored directories.  Hard link relationships of the symbolic links
   are preserved *only in the library*.  (This is because the Linux
   kernel/POSIX system calls do not allow for editing symbolic links in
   place.  They must be unlinked and remade.)  Symbolic links are
   unlinked and a new symbolic link is made then relinked.  Filename
   conflicts are resolved and reported (if a file with the same name is
   made in between moving the directory and creating the symbolic link,
   for example).

maketree()
   Return a tree generated using the library's configuration files.

ProxyLibrary
------------

ProxyLibrary is a subclass of Library for virtual FUSE mounted
libraries.  It overrides the following methods:

fix()
   Log a warning and do nothing. (Action not allowed.)

mount(path, tree)
   Log a warning and do nothing. (Action not allowed.)
