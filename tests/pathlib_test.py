import unittest
import os
import logging
import tempfile
import shutil

from dantalian import pathlib as dpath

logger = logging.getLogger(__name__)


class TestPath(unittest.TestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        os.chdir(self.root)
        os.mknod('a')
        os.mknod('a.mp3')

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def test_istag(self):
        self.assertTrue(dpath.istag('//tag'))
        self.assertTrue(dpath.istag('//tag/madoka'))
        self.assertFalse(dpath.istag('/tag'))
        self.assertFalse(dpath.istag('/tag/hi'))
        self.assertFalse(dpath.istag('tag'))
        self.assertFalse(dpath.istag('tag/bye'))

    def test_pathfromtag(self):
        r = os.getcwd()
        o = os.path.join(r, 'tag')
        self.assertEquals(dpath.pathfromtag('//tag', r), o)

    def test_tagfrompath(self):
        r = os.getcwd()
        o = '//tag'
        self.assertEquals(dpath.tagfrompath('tag', r), o)
        self.assertEquals(dpath.tagfrompath(os.path.join(r, 'tag'), r), o)

    def test_resolve_name(self):
        self.assertEquals(dpath.resolve_name(self.root, 'b'), 'b')
        self.assertEquals(dpath.resolve_name(self.root, 'a'), 'a.1')
        self.assertEquals(
            dpath.resolve_name(self.root, 'a.mp3'), 'a.1.mp3')
