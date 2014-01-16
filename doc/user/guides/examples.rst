Examples
========

Create a library::

  # Create with working directory
  $ dantalian init
  # Specify a directory
  $ dantalian init path/to/dir

Specify a library for a command to use::

  $ dantalian --root path/to/library <command>

Tag a file::

  # Specify tag absolutely
  $ dantalian tag //path/to/tag file
  # Specify tag by directory path
  $ dantalian tag path/to/tag file
  # Multiple files
  $ dantalian tag //tag file1 file2
  # Multiple tags
  $ dantalian tag -s file //tag1 //tag2

Untag a file (same as tagging)::

  $ dantalian untag //tag file1 file2
  $ dantalian untag -s file //tag1 //tag2
