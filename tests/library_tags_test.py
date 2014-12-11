"""
This module contains unit tests for dantalian.library.tags
"""

import unittest

from dantalian.library import tags

# pylint: disable=missing-docstring


class TestLibraryBase(unittest.TestCase):

    def test_is_tag(self):
        self.assertTrue(tags.is_tag('//foo/tag'))
        self.assertTrue(tags.is_tag('/////foo/tag'))
        self.assertFalse(tags.is_tag('/foo/tag'))
        self.assertFalse(tags.is_tag('foo/tag'))

    def test_path2tag(self):
        self.assertEqual(tags.path2tag('/foo', '/foo/bar'), '//bar')

    def test_tag2path(self):
        self.assertEqual(tags.tag2path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(tags.tag2path('/foo', '///bar'), '/foo/bar')

    def test_path(self):
        self.assertEqual(tags.path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(tags.path('/foo', '/bar'), '/bar')
