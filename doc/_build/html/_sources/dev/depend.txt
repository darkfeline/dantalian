Dependencies
============

These are the dependencies and the specific version numbers that I am
working on, to aid in debugging and development should version problems
arise.

- Python 3.3.2
- findutils 4.4.2
- fuse 2.9.2

For the documentation:

- Sphinx==1.1.3

You will also need a custom ctags extension for Sphinx: `ext_ctags`_

.. _ext_ctags: https://github.com/darkfeline/ext_ctags

Place ``ext_ctags.py`` in ``sphinx/ext`` wherever Sphinx is installed
for your environment.  Otherwise, you will need to remove the extension
from ``doc/config.py`` to prevent errors.
