import unittest
import os
import logging
import tempfile
import shutil

from dantalian import pathlib

logger = logging.getLogger(__name__)


class TestTagFunctions(unittest.TestCase):

    def test_istag(self):
        self.assertTrue(pathlib.istag('///tag'))
        self.assertTrue(pathlib.istag('//tag'))
        self.assertFalse(pathlib.istag('/tag'))
        self.assertFalse(pathlib.istag('tag'))

    def test_pathfromtag(self):

        root = '/foo'
        actual = pathlib.pathfromtag('//tag', root)
        expected = os.path.join(root, 'tag')
        self.assertEqual(actual, expected)

        root = '/foo/bar'
        actual = pathlib.pathfromtag('//tag1/tag2', root)
        expected = os.path.join(root, 'tag1/tag2')
        self.assertEqual(actual, expected)

    def test_tagfrompath(self):

        root = '/foo'
        actual = pathlib.tagfrompath('/foo/tag', root)
        expected = '//tag'
        self.assertEqual(actual, expected)

        root = os.getcwd()
        actual = pathlib.tagfrompath('tag', root)
        expected = '//tag'
        self.assertEqual(actual, expected)

        root = os.getcwd()
        actual = pathlib.tagfrompath('./tag', root)
        expected = '//tag'
        self.assertEqual(actual, expected)

        root = os.getcwd()
        actual = pathlib.tagfrompath('./foo/../bar/tag', root)
        expected = '//bar/tag'
        self.assertEqual(actual, expected)


class TestNameResolution(unittest.TestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        os.mknod('a')
        os.mknod('a.mp3')

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def test_resolve_name(self):
        self.assertEqual(pathlib.resolve_name(self.root, 'b'), 'b')
        self.assertEqual(pathlib.resolve_name(self.root, 'a'), 'a.1')
        self.assertEqual(pathlib.resolve_name(self.root, 'a.mp3'), 'a.1.mp3')
