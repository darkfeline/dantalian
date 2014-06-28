dantalian-untag(1) -- Untag files
=================================

SYNOPSIS
--------

| **dantalian** **untag** [*options*] *file* *tag*
| **dantalian** **untag** [*options*] *file* -t *tag*...
| **dantalian** **untag** [*options*] *tag* -f *file*...
| **dantalian** **untag** [*options*] -f *file*... -t *tag*...

DESCRIPTION
-----------

This command removes all of the given tags from all of the given files.
After calling this command, none of the files will have any hard
links in each tag's corresponding directory.

If the file was not tagged, nothing will happen.

OPTIONS
-------

**-h**, **--help**
    Print help information.
**--root**\=\ *path*
    Specify the root directory of the library to use.

EXAMPLES
--------

See the examples in dantalian-tag(1), as untag works similarly.
