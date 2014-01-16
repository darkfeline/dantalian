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

Check the :doc:`manpage </manpage>` for the available commands and their
usage.

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
