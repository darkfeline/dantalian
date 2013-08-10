Introduction
============

dantalian is a multi-dimensionally hierarchical tag-based file
organization system.  dantalian is very much for hardcore organizers
and/or technically skilled individuals, people who want maximum
flexibility in how they organize their own files.  dantalian emphasizes
transparency, consistency and well-defined behavior.

It uses hard links, by creating hard links in subdirectories ("tags").
This provides a very flexible and transparent system.

If you

- like reading specifications (in a sense)
- wouldn't trust a incompletely documented tool with organizing your
  files
- want maximum flexibility (tag hierarchy, no restrictions on tagged
  objects (*all* files *and* directories), arbitrary subsets of tags
  like unions and intersects (this tag and this tag or that tag but not
  this tag, etc.)
- want maximum scalability (hundreds of tags, thousands of tags,
  hundreds of thousands of tags, and as many files)
- want things to behave exactly with no ambiguity (everything happens
  explicitly, with no "smart" behavior, like "It looks like you want to
  do A, so I'll do A for you without telling you.")

then dantalian is for you.  On the other hand, if you

- don't like organizing your files
- don't care too much if a file accidentally gets lost or untagged or
  misplaced
- don't want to get to know your tools and just want it *to work* (most
  of the time)

then unfortunately, dantalian is *not* for you.

Features
--------

- Simple implementation
- All files (including symlinks to directories) can be tagged
  indiscriminately.
- Libraries are transparent.  You can interact with them on a basic
  level with coreutils, e.g. ``mv``, ``ls``, ``ln``.
- Libraries are portable.  Moving is as simple as rsyncing it over and
  running ``dantalian fix``.
- Files are tagged on an inode basis.
- Metadata is "stored" in the directory structure.
- Files can be moved and/or linked elsewhere without breaking anything.
- Almost no restrictions on tagged files' names.

FUSE
^^^^
FUSE mount allows the following features:

- Allows better interaction on a file system level (trivial
   interoperability with other applications)
- Virtual tag combination directories (currently only tag unions, e.g.
   AND).
- Dynamic management through socket operations.

Upcoming Features
-----------------

- Support scripts for media metadata/tags.
- Merge libraries into a single larger one (possibly irreversible).

FUSE
^^^^

- Caching to improve performance at memory cost (optional, non-cached
  mounting will still be allowed).
- Unique mount (special mount where each file only appears once, for
  doing things like deleting duplicate files, iterating over files,
  etc.).
- Special MORE directories when there is a large number of files in a
  single directory.

Requirements
------------

- Python 3
- GNU findutils
- FUSE
- a POSIX filesystem

.. warning::
   dantalian uses hard links heavily.  Make sure you are familiar with
   how hard links work.  They are very powerful, but can be messy and/or
   dangerous if you are not familiar with them.  Especially take care
   not to accidently break hard links, e.g. by copying and removing
   files.  dantalian leverages the advantages hard links provide, but
   won't protect you from yourself!
