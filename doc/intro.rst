What is Dantalian?
==================

Dantalian is a multi-dimensionally hierarchical tag-based file
organization system, born from a user's frustration with current file
organization solutions.  Dantalian is very much for hardcore organizers
and/or technically skilled individuals, people who want maximum
flexibility in how they organize their own files.  Dantalian emphasizes
transparency, consistency and well-defined behavior.

It uses hard links, by creating hard links in directories ("tags").
This provides a very flexible and transparent system.

Keep in mind that Dantalian is not designed for all users.  Dantalin is
primarily designed for power users who need powerful organization
options, but others may also find it useful (or not).

.. warning::
   dantalian uses hard links heavily.  Make sure you are familiar with
   how hard links work.  They are very powerful, but can be messy and/or
   dangerous if you are not familiar with them.  Especially take care
   not to accidently break hard links, e.g. by copying and removing
   files.  dantalian leverages the advantages hard links provide, but
   won't protect you from yourself!

Features
--------

- Simple implementation
- All files, including tags, can be tagged indiscriminately.
- Libraries are transparent.  You can interact with them on a basic
  level with coreutils, e.g. ``mv``, ``ls``, ``ln``.
- Libraries are portable.  Moving is as simple as rsyncing it over and
  running ``dantalian fix``.
- Files are tagged on an inode basis.
- Metadata is "stored" in the directory structure.
- Files can be moved and/or linked elsewhere without breaking anything.
- Almost no restrictions on tagged files' names.
- Tags can be organized hierarchically.

With FUSE
^^^^^^^^^

- Allows easy interaction on a file system level (trivial
  interoperability with other applications).
- Special virtual 'query' tag directories (currently only tag unions,
  e.g. AND).
- Dynamic management through socket operations.

Upcoming Features
-----------------

- Support scripts for media metadata/tags.
- Merge libraries into a single larger one (possibly irreversible).

With FUSE
^^^^^^^^^

- Caching to improve performance at memory cost (optional, non-cached
  mounting will still be allowed).
- Unique mount (special mount where each file only appears once, for
  doing things like deleting duplicate files, iterating over files,
  etc.).
- Special MORE directories when there is a large number of files in a
  single directory.

Requirements
------------

- `Python 3`_
- `GNU findutils`_
- FUSE_ (Optional, but needed for FUSE features)

.. _Python 3: http://www.python.org/
.. _FUSE: http://fuse.sourceforge.net/
.. _GNU findutils: https://www.gnu.org/software/findutils/
