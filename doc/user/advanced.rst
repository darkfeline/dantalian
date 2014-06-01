Advanced Usage
==============

If you want to integrate Dantalian into other scripts, frameworks, or
programs, you should use Dantalian's Python library instead of calling
the ``dantalian`` command line script.

Comprehensive documentation of Dantalian's Python library can be found
in (and is) the source code.

What follows is a quick rundown of basic usage.

Generally, you will use ``open_library`` in ``dantalian.library`` to
load the library as a Python object, then call the methods on the
library object that correspond to Dantalian commands.  More advanced
scripting and/or optimization will require digging deeper into the
source code (and, likely, having to write a bit of stuff yourself).
