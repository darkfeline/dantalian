.. _library spec:

Library Specification
=====================

dantalian is an implementation of the dantalian library, an abstract
interface.  Much like how POSIX system calls define an interface
providing a standard file system interface abstraction, the dantalian
library defines a standard interface for a multidimensionally
hierarchical tagging system.

dantalian provides a transparent implementation of the library that lies
closely on top of the underlying file system.  Details pertaining to
dantalian's library implementation will be listed separately below in
the notes.

Library Sublayer
-----------------

Libraries require a single POSIX filesystem underneath them to manage
the files.  Libraries only manage the tag metadata.

.. note::

   dantalian's implementation anchors the library on a root directory
   given by an absolute path on the file system, but the general library
   specification has no such requirement.

Library objects
---------------

Libraries interact with files (including directories) and tags.  Both
are described with strings.

Tags start with ``//``, similar to absolute paths, but doubled to
distinguish them.  Like POSIX paths, parent and child tags are separated
with ``/``.  ``/`` is not allowed in tag names, but all other characters
are legal.

Files are identified by their path, in standard POSIX format.  However,
paths starting with ``//`` are not legal, since that is reserved for
tags.  Libraries handle files by their inode.  Thus, if a file is moved,
it maintains its status in the library, but must be referred to with its
new path.

.. note::

   Tags are directories in dantalian's library implementation.  Thus,
   tags and directories (as files) may be referenced interchangeably as
   a file or a tag, respectively.

   Directories are considered tags relative to the library root.  Thus,
   a directory ``albums`` in the root directory is synonymous with tag
   ``//albums``, and a directory ``artists`` in ``albums`` with tag
   ``//albums/artists``.

   Due to dantalian's implementation, the special root tag ``//`` exists
   as an implementation detail.  The only documented appearance of the
   root tag is when calling
   :meth:`dantalian.library.BaseLibrary.listtag()`, which will include
   the root tag if the file is hard linked under the library root
   directory.  The root tag will work everywhere a tag will, but again,
   is an implementation detail specific to dantalian's implementation.

Tagging
-------

Libraries allow objects to be associated with tags and track these
associations.

Both files and tags may be tagged.  Each object can have any number and
any combination of tags.  Each object can only be tagged with a given
tag once; the relationship is binary, either tagged or untagged.  Tags
can be tagged with themselves.

.. note::

   Directories can only be tagged once by virtue of common file system
   limitations.  Symbolic links act identically to files.  In order to
   tag a directory multiple times in dantalian's library implementation,
   the directory must be converted (stored in a designated location and
   replaced with a corresponding symbolic link).  If a file system
   were to support directory hard links, then the library specification
   applies normally.

.. _library class:

Library class and methods
-------------------------

The library interface is defined in the
:class:`dantalian.library.BaseLibrary` class.  Library implementation
must implement the following methods:

.. method:: tag(file, tag)
   :noindex:

   `file` should be tagged with `tag` after call, regardless of whether
   it was before.

.. method:: untag(file, tag)
   :noindex:

   `file` should not be tagged with `tag` after call, regardless of
   whether it was before.

.. method:: mktag(tag)
   :noindex:

   `tag` is created.  Do nothing if it exists.

.. method:: rmtag(tag)
   :noindex:

   `tag` is removed.  Do nothing if it doesn't exist.

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

Implementation specifics
------------------------

This section contains additional information about dantalian's library
implementation.

Directories are tags, and vice versa.  Objects tagged with a given tag
are hard linked under the respective directory.  A file can appear
within a directory multiple times; such a file will be considered as
tagged once with the corresponding tag.

Due to practical reasons, there is a directory ``.dantalian`` in the
library root directory reserved for internal use.  It is treated
normally, i.e., as a directory and as a tag, but in almost all cases it
should not be used as a tag and should be considered an implementation
detail.

Everywhere a tag is needed in a library's method calls, a path to a directory
can be substituted.
