Introduction
============

dantalian is a tag-based file organization system, much like Tagsistant.
dantalian is very much for hardcore organizers and/or technically skilled
individuals, people who want maximum flexibility in how they organize their own
files.  dantalian emphasizes transparency, consistency and well-defined
behavior.

It uses hard links, by creating hard links in subdirectories ("tags").  This
provides a very flexible and transparent system.

If you

- like reading specifications (in a sense)
- wouldn't trust a incompletely documented tool with organizing your files
- want maximum flexibility (tag hierarchy, no restrictions on tagged objects
  (files and directories), arbitrary subsets of tags like unions and intersects
  (this tag and this tag or that tag but not this tag, etc.)
- want maximum scalability (hundreds of tags, thousands of tags, hundred
  thousands of tags, and as many files)
- want things to behave exactly with no ambiguity

then dantalian is for you.  On the other hand, if you

- don't like organizing your files
- don't care too much if a file accidentally gets lost or untagged or misplaced
- don't want to get to know your tools and just want it *to work* (I like to
  call it Apple user mentality =))

then unfortunately, dantalian is *not* for you.

Features
--------

- Simple implementation
- All files (including symlinks to directories) can be tagged indiscriminately.
- Libraries is transparent.  You can interact with it on a basic level with
  coreutils, e.g. ``mv``, ``ls``, ``ln``.
- Libraries are portable.  Moving is as simple as rsyncing it over and running
  ``dantalian fix``.
- Files are tagged on an inode basis.
- Metadata is "stored" in the directory structure.
- Files can be moved and/or linked elsewhere without breaking anything.
- Almost no restrictions on tagged files' names.

FUSE
^^^^
FUSE mount allows the following features:

  - Allows better interaction on a file system level (trivial interoperability
    with other applications)
  - Virtual tag combination directories (currently only tag unions, e.g. AND).

Upcoming Features
-----------------

- Support scripts for media metadata/tags.
- Remove converted directories that are no longer referenced.

FUSE
^^^^

- Dynamic management through socket operations.
- Caching to improve performance at memory cost (optional, non-cached mounting
  will still be allowed).
- Merge libraries into a single larger one (possibly irreversible).
- Unique mount (special mount where each file only appears once, for doing
  things like deleting duplicate files, iterating over files, etc.).
- Special MORE directories for large number of files in a single directory.


Requirements
------------

- GNU findutils
- fuse

.. note::
   dantalian uses hard links heavily.  Make sure you are familiar with how hard
   links work.  They are very powerful, but can be messy and/or dangerous if
   you are not familiar with them.  Especially take care not to accidently
   break hard links, e.g. by copying and removing files.  dantalian
   leverages the advantages hard links provide, but won't protect you from
   yourself!
