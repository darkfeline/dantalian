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
- sphinxcontrib-napoleon==0.2.1

.. note::

   At the moment, sphinxcontrib-napoleon is not Python 3 compatible, so
   I've patched a `custom version`__.

   .. __: https://github.com/darkfeline/sphinxcontrib-napoleon

If you want, you can use a custom ctags extension for Sphinx:
`ext_ctags`_

.. _ext_ctags: https://github.com/darkfeline/ext_ctags

Place ``ext_ctags.py`` in ``sphinx/ext`` wherever Sphinx is installed
for your environment.
