"""
This module contains a TestCase class that has been extended with assertion
methods.
"""

import unittest
import os

from dantalian.library import base as library


class ExtendedTestCase(unittest.TestCase):

    """TestCase class extended with helpful assert methods."""

    # pylint: disable=invalid-name

    def assertSameFile(self, file1, file2):
        """Assert both files are the same by inode."""
        self.assertTrue(os.path.samefile(file1, file2))

    def assertNotSameFile(self, file1, file2):
        """Assert files are not the same.

        Assertion fails if first file does not exist.
        """
        self.assertTrue(os.path.exists(file1))
        if os.path.exists(file2):
            self.assertFalse(os.path.samefile(file1, file2))

    def assertSameTree(self, node1, node2):
        """Assert two query node trees are equal."""
        self.assertEqual(node1, node2)
        if isinstance(node1, library.GroupNode):
            for i in range(len(node1.children)):
                self.assertSameTree(node1.children[i], node2.children[i])
