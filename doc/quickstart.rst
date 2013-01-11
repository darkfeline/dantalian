Quickstart Guide
================

hitagiFS is a tag-based "soft filesystem".  It provides a wrapper interface to
the underlying filesystem.  It requires hard links and expects to be on one
device/partition (can't hard link across devices or partitions).

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

Navigate into the directory.  hitagiFS will look through parent directories to
find a hitagifs to work with, but you can also specify a specific directory::


    $ hfs --root=/path/to/root <command>

Make a few tags (tags are directories!)::

    $ mkdir -p pics/kitty
    $ mkdir -p pics/fruit
    $ mkdir -p food
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   └── fruit
    ├── food
    └── 1.jpg

Tag a few photos::

    $ hfs tag pics/kitty 1.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 1.jpg
    │   └── fruit
    ├── food
    └── 1.jpg
    $ hfs tag food 1.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 1.jpg
    │   └── fruit
    ├── food
    │   └── 1.jpg
    └── 1.jpg

Untag::

    $ hfs untag food 1.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 1.jpg
    │   └── fruit
    ├── food
    └── 1.jpg

Rename::

    $ hfs rename 1.jpg 2.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 2.jpg
    │   └── fruit
    ├── food
    └── 2.jpg

Convert a directory so you can tag it::

    $ hfs convert pics/fruit
    $ hfs tag food pics/fruit
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 2.jpg
    │   └── fruit
    ├── food
    │   └── fruit
    └── 2.jpg
    $ hfs tag pics/fruit 2.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   └── 2.jpg
    │   └── fruit
    │       └── 2.jpg
    ├── food
    │   └── fruit
    │       └── 2.jpg
    └── 2.jpg

Delete a file::

    $ hfs rm 2.jpg
    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   └── fruit
    └── food
        └── fruit

You can also look for multiple tags at once::

    $ tree .
    .
    ├── pics
    │   ├── kitty
    │   │   ├── 1.jpg
    │   │   └── 2.jpg
    │   └── fruit
    └── food
        └── 2.jpg
    $ hfs find pics/kitty
    1.jpg
    2.jpg
    $ hfs find pics/kitty food
    2.jpg

Make sure to check the rest of the documentation for specifics.
