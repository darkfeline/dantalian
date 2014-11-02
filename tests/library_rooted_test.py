"""
This module contains unit tests for dantalian.library.rooted
"""

import os
import unittest

from dantalian.library import rooted

# pylint: disable=missing-docstring,too-many-public-methods


class TestLibraryBase(unittest.TestCase):

    def test_is_tag(self):
        self.assertTrue(rooted.is_tag('//foo/tag'))
        self.assertTrue(rooted.is_tag('/////foo/tag'))
        self.assertFalse(rooted.is_tag('/foo/tag'))
        self.assertFalse(rooted.is_tag('foo/tag'))

    def test_path2tag(self):
        self.assertEqual(rooted.path2tag('/foo', '/foo/bar'), '//bar')

    def test_tag2path(self):
        self.assertEqual(rooted.tag2path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(rooted.tag2path('/foo', '///bar'), '/foo/bar')

    def test_path(self):
        self.assertEqual(rooted.path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(rooted.path('/foo', '/bar'), '/bar')
