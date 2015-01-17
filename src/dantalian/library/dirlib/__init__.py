"""This package contains library operations for directory tagging.

These are split into two modules, for things that handle internal and external
tags, respectively.

Specification
-------------

A directory may contain a link to a file with the filename `.dtags`.  The file
to which this link points contains tagnames which are each terminated with a
single newline.

A directory is internally tagged with a tagname if and only if its `.dtags`
file contains that tagname.

A directory A is externally tagged with a directory B if and only if there
exists at least one symlink in B that refers to A.

A directory A is externally tagged at pathname B if and only if B refers to a
symlink that refers to A.

Given a rootpath, a directory A being internally tagged with a tagname B is
equivalent to A being externally tagged at the pathname which is equivalent
to B.

Dantalian uses both internal and external tags, but internal tags are
considered more stable and reliable than external tags.

"""

# pylint: disable=wildcard-import

from .internal import *
from .external import *
