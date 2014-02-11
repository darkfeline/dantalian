dantalian - Dantalian CLI script
================================

SYNOPSIS
--------

**dantalian** [*OPTION*]... *COMMAND* [*ARGS*]...

DESCRIPTION
-----------

**dantalian** is the command line utility for Dantalian, a transparent
tag-based file organization system.

Comprehensive documentation can be found online at
https://dantalian.readthedocs.org/ (note the version).  The
documentation may also be distributed and installed locally, in which
case it can probably be found in the usual location.

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

Note that global options must come before the command, and command
specific options and arguments come after the command.

COMMANDS
--------

There are three types of commands: universal commands, library commands,
and socket commands.

Universal commands are used without a reference to any specific library.

Library commands are used with a library, either detected automatically
or specified with the ``--root`` global option.  These either affect or
query against the given library.

Socket commands can only be used with a FUSE-mounted library.  Like
library commands, they take a library, however, socket commands interact
dynamically with the library's FUSE representation model.

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

mktag
   Usage: **dantalian mktag** *TAG*

   Make TAG.

rmtag
   Usage: **dantalian rmtag** *TAG*

   Remove TAG.

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

   Renames all hard links of FILE to NEW.  File name conflicts are
   resolved and reported.  Any errors will be reported and renaming will
   resume for remaining hard links.

convert
   Usage: **dantalian convert** *DIR*...


   Store directory dir internally and replace the original with a
   symbolic link with the same name pointing to the absolute path of the
   stored directory. Resolve name conflict if necessary (if a file with
   the same name is made in between moving the directory and creating
   the symbolic link, for example).

fix
   Usage: **dantalian fix**


   Fixes symlinks after the library has been moved.  If it hasn't been
   moved, does nothing.

   Fix the absolute paths of symbolic links in the library to internally
   stored directories after the library’s path has been changed. Hard
   link relationships of the symbolic links are preserved *only in the
   library*.  (This is because the Linux kernel/POSIX system calls do
   not allow for editing symbolic links in place. They must be unlinked
   and remade.) Symbolic links are unlinked and a new symbolic link is
   made then relinked. Filename conflicts are resolved and reported (if
   a file with the same name is made in between deleting and creating
   the symbolic link, for example).

clean
   Usage: **dantalian clean**

   Clean converted directories.  Delete any converted directories which
   no longer have any symlinks in the library reference it.

mount
   Usage: **dantalian mount** *DIR*

   Mounts a virtual FUSE file system representation of the library at
   DIR.

FUSE
^^^^

mknode
   Usage: **dantalian mknode** *PATH* *TAGS*...


   Make a TagNode at PATH using the given TAGS.  Make any intermediary
   Nodes as needed.

rmnode
   Usage: **dantalian mknode** *PATH* *TAGS*...

   Remove a Node or TagNode

CONFIGURATION FILES
-------------------

| *.dantalian/mount*
| *.dantalian/mount_custom*
