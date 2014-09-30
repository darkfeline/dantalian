"""
This module contains a TestCase class that has been extended with assertion
methods.
"""

import unittest
import tempfile
import shutil
import os

from dantalian.library import base as library


class ExtendedTestCase(unittest.TestCase):

    def assertSameFile(self, a, b):
        self.assertTrue(os.path.samefile(a, b))

    def assertNotSameFile(self, a, b):
        if os.path.exists(a) and os.path.exists(b):
            self.assertFalse(os.path.samefile(a, b))
        else:
            self.assertFalse(not os.path.exists(a) and not os.path.exists(b))

    def assertSameTree(self, a, b):
        """Assert two query node trees are equal."""
        if ((isinstance(a, library.AndNode) and
             isinstance(b, library.AndNode)) or
            (isinstance(a, library.OrNode) and isinstance(b, library.OrNode))):
            self.assertEqual(len(a.children), len(b.children),
                             msg="{} {}".format(a.children, b.children))
            for i in range(len(a.children)):
                self.assertSameTree(a.children[i], b.children[i])
        else:
            self.assertTrue(isinstance(a, library.DirNode) and
                            isinstance(b, library.DirNode))
            self.assertEqual(a.dirpath, b.dirpath)
