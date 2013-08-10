.. _names:

Names and Paths
===============

Files
-----

Everything is done internally via inodes, so all operations take
filenames only as a way to indicate a particular file/inode, and
dantalian works with that.  Thus, file naming is for the most part a
concern for the user only.

.. _rename_alg:

File Renaming Algorithm
-----------------------

When dantalian needs to add a file to a directory (e.g., when renaming
or tagging), it will attempt to use the name of the file directly.  If
it runs into a filename/path conflict, it will then attempt to generate
a new name using the algorithm described below::

   def resolve(dir, name):
      base, extension = split_extension(name)
      for i=1; ; i++:
         new_name = base + '.' + i + '.' + extension
         if is_okay(dir, new_name):
            return new_name

If between generating the new name and using it the name becomes
unavailable, dantalian will try to generate a name again using the
original name.
