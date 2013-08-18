import unittest
import os
import logging

from dantalian import path as dpath

logger = logging.getLogger(__name__)


class TestPath(unittest.TestCase):

    def test_pathfromtag(self):
        r = os.getcwd()
        o = os.path.join(r, 'tag')
        self.assertEquals(dpath.pathfromtag('/tag', r), o)
        self.assertEquals(dpath.pathfromtag('tag', r), o)
