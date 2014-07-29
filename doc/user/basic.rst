Basic Usage
===========

Dantalian is essentially a group of scripts to help manage hard link
tagging as described previously.

Libraries
---------

Libraries are used to designate root directories as an anchor point for
tags and file organization.  They can be identified by the special
``.dantalian`` directory that they contain.

For more information about libraries, see :doc:`library`.

Creating libraries
^^^^^^^^^^^^^^^^^^

Libraries can be initialized with the command :command:`dantalian
init`.  This will create the library in the working directory.
Alternatively, pass the path where you want to create the library::

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
both ``1.txt`` are hard links to the same file) which is tagged
(perhaps incorrectly) with both ``//even`` and ``//odd`` tags.

Tags can be referred to in two ways, by the path to its directory,
whether relative or absolute, or by its tag qualifier.  A tag qualifier
is simply the path of its directory, relative to the library root,
prepended by ``//``.

For example, given the following::

   library
   └── tag1
      └── tag2

if the current working directory is tag1, we can refer to tag2 as
``tag2`` (relative path) or ``//tag1/tag2`` (tag qualifier).

See also :manpage:`dantalian-concepts(1)`.

Basic Commands
--------------

Check the man pages for the command reference.

Tagging and Untagging
^^^^^^^^^^^^^^^^^^^^^

Tags can be created and removed using the commands :command:`dantalian
mktag` and :command:`dantalian rmtag`.  This can be done manually using
the standard utility :command:`mkdir`.

::

   $ dantalian mktag //kitties
   $ dantalian rmtag //kitties
   $ mkdir kitties
   $ rmdir kitties

Note that :command:`mktag` and :command:`rmtag` only take tag
qualifiers, and :command:`mkdir` and :command:`rmdir` only take
pathnames.

Tags can be applied to and removed from files using :command:`dantalian
tag` and :command:`dantalian untag` (see :manpage:`dantalian-tag(1)`
and :manpage:`dantalian-untag(1)`).  This can also be done manually by
manipulating the links with :command:`ln` and :command:`rm`.

::

    $ dantalian tag file1 tag1
    $ dantalian tag file1 -t tag1 tag2 tag3
    $ dantalian tag tag1 -f file1 file2 file3
    $ dantalian tag -f file1 file2 -t tag1 tag2

    $ dantalian untag file1 tag1
    $ dantalian untag file1 -t tag1 tag2 tag3
    $ dantalian untag tag1 -f file1 file2 file3
    $ dantalian untag -f file1 file2 -t tag1 tag2

Basic Queries
^^^^^^^^^^^^^

You can list the tags of a file with :command:`dantalian tags`::

    $ dantalian tags file1
    //spam
    //eggs

You can perform an AND search on tags with :command:`dantalian find`::

    $ dantalian find //spam //eggs
    /home/foo/library/spam/file1

You can list the files of a single tag simply using :command:`ls` in
the respective directory.  You can do this with AND tag queries using
Dantalian FUSE features.
