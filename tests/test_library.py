import unittest
import tempfile
import shutil
import os
import logging

from dantalian import library

logger = logging.getLogger(__name__)


class TestLibraryMethods(unittest.TestCase):

    def setUp(self):
        self._olddir = os.getcwd()
        self.root = tempfile.mkdtemp()
        r = os.path.join(self.root, 'library')
        os.mkdir(r)
        os.chdir(r)
        os.makedirs(os.path.join('A', 'D'))
        os.makedirs('B')
        os.makedirs('C')
        os.mknod('a')
        os.mknod('b')
        os.link('b', os.path.join('C', 'b'))
        self.library = library.init_library(r)
        os.chdir(self.root)

    def tearDown(self):
        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def assertTagged(self, a, b):
        self.assertTrue(os.path.samefile(a, b))

    def assertNotTagged(self, a, b):
        if os.path.exists(a) and os.path.exists(b):
            self.assertFalse(os.path.samefile(a, b))
        elif not os.path.exists(a) and not os.path.exists(b):
            self.assertTrue(False)

    def assertSameTags(self, a, b):
        self.assertEqual(a, b)
        self.assertEqual(set(a), set(b))

    def test_tag(self):
        l = self.library
        os.chdir('library')
        l.tag('a', '/A')
        self.assertTagged(os.path.join('A', 'a'), 'a')
        l.tag('a', '/A/D')
        self.assertTagged(os.path.join('A', 'D', 'a'), 'a')

    def test_untag(self):
        l = self.library
        os.chdir('library')
        self.assertTagged(os.path.join('C', 'b'), 'b')
        l.untag('b', '/C')
        self.assertNotTagged(os.path.join('C', 'b'), 'b')

    def test_listtags(self):
        l = self.library
        os.chdir('library')
        self.assertSameTags(l.listtags('a'), ['/'])
        self.assertSameTags(l.listtags('b'), ['/', '/C'])
        l.tag('b', '/A')
        self.assertSameTags(l.listtags('b'), ['/', '/C', '/A'])

    def test_convert(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        p = os.path.join(self.root, l.dirsdir(l.root), 'A')
        self.assertTrue(os.path.isdir(p))
        self.assertEquals(os.readlink('A'), p)
