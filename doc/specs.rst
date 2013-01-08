******
Design
******

Specification
=============

Tags
----

Files and directories can be assigned any number of tags.  If there's a path
collision between a directory and tag, the tag takes precedence, and a warning
will be raised.  Ideally, hitagiFS will detect when an action will cause this
and refuse to perform the action.

Directory hierarchy
-------------------

Tags are organized in a standard tree hierarchy.  Files and directories with
the given tag will appear under the tag in the hierarchy.

Interaction
-----------

All interactions with the mounted hitagiFS will interact with the virtual file
system.  Creating a directory creates a tag.  Adding, moving, deleting objects
(actual files and directories) changes that object's tags.

Implementation
==============

hitagiFS will be implemented in Python 2 using llfuse.  Metadata will be stored
in a database (probably sqlite3).

Example
=======

``/home/fag/file`` is tagged with ``loli``, ``2hu``, ``halloween``.
hitagiFS is mounted at ``/hitagi``.

Tag hierarchy::

    /
    /themes
    /themes/loli
    /themes/halloween
    /sauce
    /sauce/2hu

::

    $ ls /hitagi/
    themes/
    sauce/
    $ ls /hitagi/themes
    loli/
    halloween/
    $ ls /hitagi/themes/loli
    file
    $ ls /hitagi/themes/halloween
    file
