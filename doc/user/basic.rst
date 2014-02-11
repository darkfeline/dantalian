Basic Usage
===========

Libraries
---------

Dantalian uses libraries to designate root directories in which files
are organized.

Libraries can be identified by the special ``.dantalian`` directory that
they contain.

For much more information about libraries, see :ref:`libraries`.

Creating libraries
^^^^^^^^^^^^^^^^^^

Libraries can be initialized with the command ``dantalian init``.  This
will create the library in the working directory.  Alternatively, pass
the path where you want to create the library::

   $ dantalian init path/to/directory

Tags
----

In Dantalian, tags are directories.  A file has a tag if it has a hard
link in the directory corresponding to that tag.

For example, in the following library::

   .
   ├── even
   │   └── 1.txt
   └── odd
       └── 1.txt

There are two tags, ``//even`` and ``//odd``, and one file (assuming
both ``1.txt`` are hard links to the same file) which is tagged (perhaps
incorrectly) with both ``//even`` and ``//odd`` tags.

Tags can be referred to in two ways, by the path to its directory,
whether relative or absolute, or by its unique tag qualifier.  A tag
qualifier is simply the path of its directory, relative to the library
root, prepended by ``//``.

For example, given the following::

   library
   └── tag1
      └── tag2

if the current working directory is tag1, we can refer to tag2 as
``tag2`` (relative path) or ``//tag1/tag2`` (tag qualifier).

Basic Commands
--------------

See the :ref:`commands` for a full reference to Dantalian's commands.

Tagging and Untagging
^^^^^^^^^^^^^^^^^^^^^

Tags can be created and removed using the commands ``dantalian mktag``
and ``dantalian rmtag``.  This can be done manually using the standard
utility ``mkdir``.

::

   dantalian mktag kitties
   dantalian rmtag kitties
   mkdir kitties
   rmdir kitties

Note that the commands are not entirely interchangeable, since you can
use unique tag qualifiers with ``dantalian mktag`` and family, but not
mkdir::

   dantalian mktag //path/to/tag/from/library/root


Tags can be applied to and removed from files using ``dantalian tag``
and ``dantalian untag``, with support for tagging multiple files with
one tag (by default), or for tagging one file with multiple tags (by
passing ``-s``; see the :ref:`commands`.).  This can be done manually
with ``ln`` and ``rm``.

Basic Queries
^^^^^^^^^^^^^

You can list the tags of a file with ``dantalian tags``.

You can perform an AND search on tags with ``dantalin find``.

You can list the files of a single tag simply using ``ls`` in the
respective directory.  You can do this with AND tag queries using
Dantalian FUSE features.
