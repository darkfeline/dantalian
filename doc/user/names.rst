.. _names:

Names and Paths
===============

Files
-----

Everything is done internally via inodes, so all operations take
filenames only as a way to indicate a particular file/inode, and
Dantalian works with that.  Thus, file naming is for the most part a
concern for the user only.

.. _rename_alg:

File Renaming Algorithm
-----------------------

When Dantalian needs to add a file to a directory (e.g., when renaming
or tagging), it will attempt to use the name of the file directly.  If
it runs into a filename/path conflict, it will then attempt to generate
a new name using the algorithm described below::

   def resolve(dir, name):
      base, extension = split_extension(name)
      for i=1; ; i++:
         new_name = '.'.join([base, i, extension])
         if is_okay(dir, new_name):
            return new_name

For example, Dantalian will try, in order::

   file.mp3
   file.1.mp3
   file.2.mp3
   file.3.mp3
   ...

If between generating the new name and using it the name becomes
unavailable, Dantalian will try to generate a name again from the
beginning.

FUSE Name Collision Resolution
------------------------------

When file names are projected in a FUSE mounted library, there is a high
chance of name collisions, in which case the virtual names of affected
files are changed with the following algorithm::

   def fuse_resolve(name, path):
      base, extension = split_extension(name)
      new_name = '.'.join([base, get_inode_number(path), extension])
      return new_name

In practice there will be no further name collisions, but if there are,
then name collision resolution will be propagated outward until there
are no name collisions.  This state is guaranteed as file systems cannot
assign the same inode number to two different files.

Node names use ``node`` instead of an inode number for resolution.
