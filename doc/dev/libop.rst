Library Implementation
======================

This section documents dantalian's library implementation.  See
:ref:`library spec` for a reference to the library specification.

Library
-------

Library is the actual implementation that dantalian provides.  It
implements the following public methods and invariants in addition to
those described in BaseFSLibrary (Filename/path conflicts will be
resolved according to :ref:`rename_alg`.):

.. note::
   dantalian respects symbolic links to directories outside of the
   library (Internal symbolic links should always be converted by
   dantalian.  Handmade symbolic links to library-internal paths subject
   to breakage and Armageddon.).  For simple operations, dantalian will
   act as though these directories are a part of the library.  For
   complex operations, these external directories will be ignored (This
   is because dantalian is not really descending symbolic links, but
   only acting on the directories stored internally. This simulates only
   descending into internal symbolic links.).  The latter case will be
   noted below if applicable.

.. method:: tag(file, tag)
   :noindex:

   If `file` does not have a hard link under the `tag` directory, make
   one.  `file` has at least one hard link under the `tag` directory
   after call.

.. method:: untag(file, tag)
   :noindex:

   `file` should not be tagged with `tag` after call, regardless of
   whether it was before.

.. method:: listtags(file)
   :noindex:

   Return a list of all of the tags of `file`.

.. method:: find(tags)
   :noindex:

   Return a list of files that have all of the given tags in `tags`.

.. method:: mount(path, tree)
   :noindex:

   Mount a virtual representation of the library representation `tree`
   at `path`.

.. method:: convert(dir)
   :noindex:

   Store directory `dir` internally and replace the original with a
   symbolic link with the same name pointing to the absolute path of the
   stored directory.  Resolve name conflict if necessary (if a file with
   the same name is made in between moving the directory and creating
   the symbolic link, for example).

.. method:: cleandirs()
   :noindex:

   Remove all directories stored internally that no longer have any
   symbolic links referring to them in the library.

.. method:: rm(file)
   :noindex:

   Remove all hard links to `file` in the library.  Any errors will be
   reported and removal will resume for remaining hard links.

.. note::

   :meth:`rm` does not descend into symbolic links to external
   directories.

.. method:: rename(file, new)
   :noindex:

   Rename all hard links to `file` in the library to `new`.  File name
   conflicts are resolved and reported.  Any errors
   will be reported and renaming will resume for remaining hard links.

.. note::

   :meth:`rename` does not descend into symbolic links to external
   directories.

.. method:: fix()
   :noindex:

   Fix the absolute paths of symbolic links in the library to internally
   stored directories.  Hard link relationships of the symbolic links
   are preserved *only in the library*.  (This is because the Linux
   kernel/POSIX system calls do not allow for editing symbolic links in
   place.  They must be unlinked and remade.)  Symbolic links are
   unlinked and a new symbolic link is made then relinked.  Filename
   conflicts are resolved and reported (if a file with the same name is
   made in between deleting and creating the symbolic link, for
   example).

.. method:: maketree()

   Return a tree generated using the library's configuration files.

ProxyLibrary
------------

ProxyLibrary is a subclass of Library for virtual FUSE mounted
libraries.  It overrides the following methods:

.. method:: fix()
   :noindex:

   Log a warning and do nothing. (Action not allowed.)

.. method:: mount(path, tree)
   :noindex:

   Log a warning and do nothing. (Action not allowed.)
