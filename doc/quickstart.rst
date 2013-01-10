Quickstart Guide
================

.. warning::
    hitagiFS is still in development/unstable.  I've preliminarily tested it,
    so it shouldn't e.g. delete ``/``, but just in case, make the necessary
    preparations before using.

hitagiFS is a tag-based "soft filesystem".  It provides a wrapper interface to
the underlying filesystem.  It requires hard links, and expects to be on one
device/partition (can't hard link across devices or partitions), and expects to
be in a constant location (don't move around).

Installing is as easy as::

    python setup.py install

No dependencies! Except the following:

* ``find`` utility should be installed (I can't imagine why not, but...)
* You need Sphinx to build the documentation (It's already built, though)

Create a new directory to hold your hitagifs::

    $ mkdir test
    $ hfs init test

or::

    $ mkdir test
    $ cd test
    $ hfs init

Navigate into the directory, and activate the hitagifs::

    $ cd test
    $ source .hitagifs/bin/activate

Your prompt should now show that it is activated::

    (hitagifs:test)$

Make a few tags (tags are directories!)::

    (hitagifs:test)$ mkdir -p pics/kitty
    (hitagifs:test)$ mkdir -p pics/fruit
    (hitagifs:test)$ mkdir -p food
    (hitagifs:test)$ tree .
    .
    ├── pics
    │   ├── kitty
    │   └── fruit
    └── food

Tag a few photos (you can nagivate somewhere else)::

    (hitagifs:test)$ cd ..
    (hitagifs:test)$ hfs tag pics/kitty 1.jpg
    (hitagifs:test)$ tree test
    test
    ├── pics
    │   ├── kitty
    │   │   └── 1.jpg
    │   └── fruit
    └── food
    (hitagifs:test)$ hfs tag food 1.jpg
    (hitagifs:test)$ tree test
    test
    ├── pics
    │   ├── kitty
    │   │   └── 1.jpg
    │   └── fruit
    └── food
        └── 1.jpg

Check the specification for all the commands and internal details.
