Quickstart Guide
================

dantalian is a tag-based "soft filesystem".  It provides a wrapper interface to
the underlying filesystem.  It requires hard links and expects to be on one
device/partition (can't hard link across devices or partitions).

Installing is as easy as::

   python setup.py install

Create a new directory to hold your library::

   $ mkdir test
   $ dantalian init test

or::

   $ mkdir test
   $ cd test
   $ dantalian init

Navigate into the directory.  dantalian will look through parent directories to
find a library to work with, but you can also specify a specific directory::


   $ dantalian --root=/path/to/root <command>

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

   $ dantalian tag pics/kitty 1.jpg
   $ tree .
   .
   ├── pics
   │   ├── kitty
   │   │   └── 1.jpg
   │   └── fruit
   ├── food
   └── 1.jpg
   $ dantalian tag food 1.jpg
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

   $ dantalian untag food 1.jpg
   $ tree .
   .
   ├── pics
   │   ├── kitty
   │   │   └── 1.jpg
   │   └── fruit
   ├── food
   └── 1.jpg

Rename::

   $ dantalian rename 1.jpg 2.jpg
   $ tree .
   .
   ├── pics
   │   ├── kitty
   │   │   └── 2.jpg
   │   └── fruit
   ├── food
   └── 2.jpg

Convert a directory so you can tag it::

   $ dantalian convert pics/fruit
   $ dantalian tag food pics/fruit
   $ tree .
   .
   ├── pics
   │   ├── kitty
   │   │   └── 2.jpg
   │   └── fruit
   ├── food
   │   └── fruit
   └── 2.jpg
   $ dantalian tag pics/fruit 2.jpg
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

   $ dantalian rm 2.jpg
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
   $ dantalian find pics/kitty
   1.jpg
   2.jpg
   $ dantalian find pics/kitty food
   2.jpg

Make sure to check the rest of the documentation for specifics.
