*****************
Command Reference
*****************

Global Syntax
=============

Dantalian commands have the following syntax::

   dantalian [GLOBAL_OPTIONS]... COMMAND [COMMAND_SPECIFIC]...

Note that global options must come before the command, and command
specific options and arguments come after the command.

Global Options
--------------

``--root ROOT``
   Specify a specific library to use.
``--loglevel LEVEL``
   Show only logged messages LEVEL and below.  Can be DEBUG, INFO, WARN,
   ERROR, or CRITICAL, case insensitive.
``--logfile FILE``
   Specify a file for log messages instead of stderr.
``--logfilter MODULE``
   Show only messages from the given dantalian module.

Commands
========

There are three types of commands: universal commands, library commands,
and socket commands.

Universal commands are used without a reference to any specific library.

Library commands are used with a library, either detected automatically
or specified with the ``--root`` global option.  These either affect or
query against the given library.

Socket commands can only be used with a FUSE-mounted library.  Like
library commands, they take a library, however, socket commands interact
dynamically with the library's FUSE representation model.

Universal Commands
------------------

init
^^^^

::

   dantalian init [DIR]

Initializes a library in DIR.  If DIR is omitted, initializes a
library in the current directory.

Library Commands
----------------

tag
^^^

::

   dantalian tag TAG FILE...

Tags FILE with TAG.  If FILE is already tagged, does nothing.  If FILE
is a directory, you'll need to convert it first (dantalian will tell you
so).  The option ``-s`` reverses TAG and FILE, for tagging a single
file with multiple tags::

   dantalian tag -s FILE TAG...

untag
^^^^^

::

   dantalian untag TAG FILE...

Removes TAG from FILE.  If FILE isn't tagged, does nothing.  Shares the
same ``-s`` option as ``tag``.

mktag
^^^^^

::

   dantalian mktag TAG

Makes TAG.

rmtag
^^^^^

::

   dantalian rmtag TAG

Removes TAG.

tags
^^^^

::

   dantalian tags FILE

Lists all the tags of FILE.

find
^^^^

::

   dantalian find TAG...

Intersection tag search.  Lists all files that have all of the given
tags.  Lists files by the path to the hard link under the first tag
given.

rm
^^

::

   dantalian rm FILE...

Removes the files given.  That is, removes all hard links to the given
files in the library.  Hard links outside of the library are unaffected.

rename
^^^^^^

::

   dantalian rename FILE NEW

Renames all hard links of FILE to NEW.  File name conflicts are resolved
and reported.  Any errors will be reported and renaming will resume for
remaining hard links.

convert
^^^^^^^

::

   dantalian convert DIR...

Converts directories so they can be tagged.

Store directory dir internally and replace the original with a symbolic
link with the same name pointing to the absolute path of the stored
directory. Resolve name conflict if necessary (if a file with the same
name is made in between moving the directory and creating the symbolic
link, for example).

fix
^^^

::

   dantalian fix

Fixes symlinks after the library has been moved.  If it hasn't been
moved, does nothing.

Fix the absolute paths of symbolic links in the library to internally
stored directories after the library’s path has been changed. Hard link
relationships of the symbolic links are preserved *only in the library*.
(This is because the Linux kernel/POSIX system calls do not allow for
editing symbolic links in place. They must be unlinked and remade.)
Symbolic links are unlinked and a new symbolic link is made then
relinked. Filename conflicts are resolved and reported (if a file with
the same name is made in between deleting and creating the symbolic
link, for example).

clean
^^^^^

::

   dantalian clean

Clean converted directories.  Delete any converted directories which no
longer have any symlinks in the library reference it.

mount
^^^^^

::

   dantalian mount DIR

Mounts a virtual FUSE file system representation of the library at DIR.

Socket Commands
---------------

mknode
^^^^^^

::

   dantalian mknode PATH TAGS...

Make a TagNode at PATH using the given TAGS.  Make any intermediary
Nodes as needed.

rmnode
^^^^^^

::

   dantalian rmnode PATH

Remove a Node or TagNode at PATH.
