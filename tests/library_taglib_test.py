"""
This module contains unit tests for dantalian.library.taglib
"""

import os
import shutil
import tempfile
import unittest

from dantalian.library import taglib

# pylint: disable=missing-docstring


class TestLibraryTags(unittest.TestCase):

    def test_is_tag(self):
        self.assertTrue(taglib.is_tag('//foo/tag'))
        self.assertTrue(taglib.is_tag('/////foo/tag'))
        self.assertFalse(taglib.is_tag('/foo/tag'))
        self.assertFalse(taglib.is_tag('foo/tag'))

    def test_path2tag(self):
        self.assertEqual(taglib.path2tag('/foo', '/foo/bar'), '//bar')

    def test_tag2path(self):
        self.assertEqual(taglib.tag2path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(taglib.tag2path('/foo', '///bar'), '/foo/bar')

    def test_path(self):
        self.assertEqual(taglib.path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(taglib.path('/foo', '/bar'), '/bar')


class TestLibraryRoot(unittest.TestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        os.makedirs('A/.dantalian')
        os.mknod('A/.dantalian/foo')
        os.makedirs('A/foo/bar')
        os.makedirs('B/foo/bar')

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def test_is_root(self):
        self.assertTrue(taglib.is_root('A'))
        self.assertFalse(taglib.is_root('B'))

    def test_find_root(self):
        self.assertEqual(taglib.find_root('A/foo/bar'), os.path.abspath('A'))

    def test_init_root(self):
        taglib.init_root('B')
        self.assertTrue(taglib.is_root('B'))

    def test_get_resource(self):
        self.assertEqual(taglib.get_resource('A', 'foo'), 'A/.dantalian/foo')
