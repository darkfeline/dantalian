dantalian-mktag(1) -- Make tags
===============================

SYNOPSIS
--------

**dantalian** **mktag** [*options*] *tag*...

DESCRIPTION
-----------

This command makes tags (directories).

This command only works with tag qualifiers.  If you want to work
with paths, use mkdir(1) instead.

OPTIONS
-------

-h, --help   Print help information.
--root=PATH  Specify the root directory of the library to use.

EXAMPLES
--------

Make tags::

    $ dantalian mktag //tag1 //tag2

Note that you cannot do this::

    $ dantalian mktag tag1

Instead do::

    $ mkdir tag1
