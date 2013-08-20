import unittest
import os
import logging

from dantalian import path as dpath

logger = logging.getLogger(__name__)


class TestPath(unittest.TestCase):

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
