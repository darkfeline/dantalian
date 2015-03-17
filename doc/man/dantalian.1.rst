dantalian(1) -- file management using hard links
================================================

SYNOPSIS
--------

**dantalian** [*options*] *command* [*args*]

DESCRIPTION
-----------

**dantalian** is a standalone script for accessing Dantalian functionality.

Dantalian is a Python 3 library to assist file organization and tagging using
hard links.

The commands here are generally equivalent to the respective functions in the
Dantalian library, with some command line sugar. Therefore, make sure to read
the documentation in addition to the man pages!

OPTIONS
-------

-h, --help  Print help information.

COMMANDS
--------

Base commands
^^^^^^^^^^^^^

dantalian-link(1)
    Link file or directory.

dantalian-unlink(1)
    Unlink file or directory.

dantalian-rename(1)
    Rename file or directory.

dantalian-swap(1)
    Swap symlink with its directory.

dantalian-save(1)
    Save dtags.

dantalian-load(1)
    Load dtags.

dantalian-unload(1)
    Unoad dtags.

dantalian-list(1)
    List links.

Search commands
^^^^^^^^^^^^^^^

dantalian-search(1)
    Do tag query search.

Library commands
^^^^^^^^^^^^^^^^

dantalian-init-library(1)
    Initialize library.

Tagging commands
^^^^^^^^^^^^^^^^

dantalian-tag(1)
   Tag file or directory.

dantalian-untag(1)
   Untag file or directory.

Bulk commands
^^^^^^^^^^^^^

dantalian-clean(1)
    Clean up broken symlinks.

dantalian-rename-all(1)
    Rename all links of a file.

dantalian-unlink-all(1)
    Unlink all links of a file.

dantalian-import(1)
    Import tag data.

dantalian-export(1)
    Export tag data.

SEE ALSO
--------

Online documentation
    http://dantalian.readthedocs.org/

Project website
    http://darkfeline.github.io/dantalian/
