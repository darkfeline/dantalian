.. _manpage:

dantalian - dantalian cli script
================================

SYNOPSIS
--------

**dantalian** [*OPTION*]... *COMMAND* [*ARGS*]...

DESCRIPTION
-----------

**dantalian** is the command line utility for dantalian, a transparent
tag-based file organization system.

Comprehensive documentation can be found online at
https://dantalian.readthedocs.org/ (note which version of dantalian the
documentation is for).  The documentation may also be distributed and
installed locally, in which case it can probably be found in the usual
location.

OPTIONS
-------

--root *ROOT*
   Specify a specific library to use.

--loglevel *LEVEL*
   Show only logged messages LEVEL and below.  Can be DEBUG, INFO, WARN,
   ERROR, or CRITICAL, case insensitive.
--logfile *FILE*
   Specify a file to log to instead of stderr.
--logfilter *MODULE*
   Show only messages from the given module

The last three options are for debugging purposes.  If you run into a
bug, run **dantalian** with ``--loglevel=DEBUG --logfile=output.log``
and include the log with the bug report.

COMMANDS
--------

There are three types of commands: universal, library, and fuse.
Universal commands are used without a reference to a library.  Library
commands must be used with a library (either detected automatically or
specified with ``--root``.  Fuse commands must be used with a
fuse-mounted library.

UNIVERSAL
^^^^^^^^^

init
   Usage: **dantalian init** [*DIR*]

   Creates a library in DIR.  If DIR is omitted, creates a library in
   the current directory.

LIBRARY
^^^^^^^

tag
   Usage: **dantalian tag** *TAG* *FILE*...

   Tags FILE with TAG.  If FILE is already tagged, does nothing.  If
   FILE is a directory, you'll need to convert it first.  The option
   ``-s`` reverses *TAG* and *FILE*, for tagging a single file with
   multiple tags.

untag
   Usage: **dantalian untag** *TAG* *FILE*...

   Removes TAG from FILE.  If FILE isn't tagged, does nothing.  Has the
   same ``-s`` options as **tag**

tags
   Usage: **dantalian tags** *FILE*

   Lists all the tags of FILE.

find
   Usage: **dantalian find** *TAG*...

   Intersection tag search.  Lists all files that have all of the given
   tags.  Lists files by the path to the hard link under the first tag
   given.

rm
   Usage: **dantalian rm** *FILE*...

   Removes the files given.  That is, removes all hard links to the
   given files in the library.  Hard links outside of the library are
   unaffected.

rename
   Usage: **dantalian rename** *FILE* *NEW*

   Renames all hard links of FILE to NEW.

convert
   Usage: **dantalian convert** *DIR*...

   Converts directories so they can be tagged.  (Moves directories to
   special location '.dantalian/dirs' and replaces the original with a
   symlink pointing to the absolute path).

fix
   Usage: **dantalian fix**

   Fixes symlinks after the library has been moved.  If it hasn't been
   moved, does nothing.

clean
   Usage: **dantalian clean**

   Clean converted directories.  Delete any converted directories which
   no longer have any symlinks in the library reference it.

mount
   Usage: **dantalian mount** *DIR*

   Mounts the FUSE file system at DIR according to the configuration
   files.

FUSE
^^^^

mknode
   Usage: **dantalian mknode** *PATH* *TAGS*...

   Make a TagNode

CONFIGURATION FILES
-------------------

| *.dantalian/mount*
| *.dantalian/mount_custom*
