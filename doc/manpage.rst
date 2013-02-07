hfs - hitagiFS cli script
=========================

SYNOPSIS
--------

**hfs** [*OPTION*]... *COMMAND* [*ARGS*]...

DESCRIPTION
-----------

**hfs** is the command line utility for hitagiFS, a transparent tag-based file
organization system.  hitagiFS is short for "Hierarchical Tag File System" (for
those who get the reference and need a little bit of tsundere in their lives).

Comprehensive documentation can be found online at
https://hitagifs.readthedocs.org/ (note which version of hitagiFS the
documentation is for).  The documentation may also be distributed and installed
locally, in which case it can probably be found in the usual location.

OPTIONS
-------

--loglevel *LEVEL*
   Show only logged messages LEVEL and below.  Can be DEBUG, INFO, WARN, ERROR,
   or CRITICAL, case insensitive.
--logfile *FILE*
   Specify a file to log to instead of stderr.
--logfilter *MODULE*
   Show only messages from the given module

These options are for debugging purposes.  If you run into a bug, run **hfs**
with ``--loglevel=DEBUG --logfile=output.log`` and include the log with the bug
report.

COMMANDS
--------

tag
   Usage: **hfs tag** *TAG* *FILE*...

   Tags FILE with TAG.  If FILE is already tagged, does nothing.  If FILE is a
   directory, you'll need to convert it first.

untag
   Usage: **hfs untag** *TAG* *FILE*...

   Removes TAG from FILE.  If FILE isn't tagged, does nothing.

tags
   Usage: **hfs tags** *FILE*

   Lists all the tags of FILE.

find
   Usage: **hfs find** *TAG*...

   Intersection tag search.  Lists all files that have all of the given tags.
   Lists files by the path to the hard link under the first tag given.

rm
   Usage: **hfs rm** *FILE*...

   Removes the files given.

rename
   Usage: **hfs rename** *FILE* *NEW*

   Renames all hard links of FILE to NEW.

convert
   Usage: **hfs convert** *DIR*...

   Converts directories so they can be tagged.  (Moves directories to special
   location '.hitagifs/dirs' and replaces the original with a symlink pointing
   to the absolute path).

fix
   Usage: **hfs fix**

   Fixes symlinks after the hitagiFS has been moved.  If it hasn't been moved,
   does nothing.

init
   Usage: **hfs init** [*DIR*]

   Creates a hitagifs in DIR.  If DIR is omitted, creates a hitagifs in the
   current directory.

mount
   Usage: **hfs mount**

   Mounts the FUSE file system according to the configuration files

CONFIGURATION FILES
-------------------

| *.hitagifs/mount*
| *.hitagifs/mount_custom*
