dantalian(1) -- file tagging using hard links
=============================================

SYNOPSIS
--------

**dantalian** [*options*] *command* [*args*]

DESCRIPTION
-----------

**dantalian** provides an interface to scripts that automate management
of file tagging using hard links.

OPTIONS
-------

**-h**, **--help**
    Print help information.

**-t**, **--test**\=\ *arg*
    Test

COMMANDS
--------

There are three types of commands.  Library commands require a library.
**dantalian** will search up the directory tree from the working
directory and use the first library it finds, or a library can be
specified explicitly by path.

Global commands do not require a library.  Socket commands require a
virtual FUSE library, and simply write commands to the virtual FUSE
library's command socket

LIBRARY COMMANDS
^^^^^^^^^^^^^^^^

dantalian-tag(1)
    Tag files.

dantalian-untag(1)
    Untag files.

dantalian-mktag(1)
    Make tags.

dantalian-rmtag(1)
    Remove tags.

dantalian-tags(1)
    List tags of files.

dantalian-find(1)
    Find files with tags.

dantalian-rm(1)
    Remove all tags of files.

dantalian-rename(1)
    Rename tagged file.

dantalian-convert(1)
    Convert directories into taggable symbolic links.

dantalian-revert(1)
    Revert converted directories from symbolic links.

dantalian-fix(1)
    Fix symbolic links of converted directories.

dantalian-clean(1)
    Clean stored converted directories.

dantalian-mount(1)
    Mount library as virtual FUSE library.

GLOBAL COMMANDS
^^^^^^^^^^^^^^^

dantalian-init(1)
    Initialize a library.

SOCKET COMMANDS
^^^^^^^^^^^^^^^

dantalian-mknode(1)
    Make a tag node.

dantalian-rmnode(1)
    Remove nodes.

SEE ALSO
--------

Online documentation
    http://dantalian.readthedocs.org/

Project website
    http://darkfeline.github.io/dantalian/
