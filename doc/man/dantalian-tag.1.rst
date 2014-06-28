dantalian-tag(1) -- Tag files
=============================

SYNOPSIS
--------

| **dantalian** **tag** [*options*] *file* *tag*
| **dantalian** **tag** [*options*] *file* -t *tag*...
| **dantalian** **tag** [*options*] *tag* -f *file*...
| **dantalian** **tag** [*options*] -f *file*... -t *tag*...

DESCRIPTION
-----------

This command tags all of the given files with all of the given tags.
After calling this command, all of the files will have at least one hard
link in each tag's corresponding directory.

If the file was already tagged, nothing will happen.  If it was not
tagged, this command will create the respective hard link using a name
as similar as possible to the file's name as provided to the command.

OPTIONS
-------

**-h**, **--help**
    Print help information.
**--root**\=\ *path*
    Specify the root directory of the library to use.

EXAMPLES
--------

Tagging one file with one tag::

    $ dantalian tag file1 tag1
    $ dantalian tag file1 -t tag1
    $ dantalian tag tag1 -f file1
    $ dantalian tag -f file1 -t tag1
    $ dantalian tag -t tag1 -f file1

Tagging one file with many tags::

    $ dantalian tag file1 -t tag1 tag2 tag3
    $ dantalian tag -f file1 -t tag1 tag2 tag3

Tagging many files with many tags::

    $ dantalian tag -f file1 file2 file3 -t tag1 tag2 tag3
