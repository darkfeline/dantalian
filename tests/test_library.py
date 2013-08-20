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
        l.tag('a', '//A')
        self.assertTagged(os.path.join('A', 'a'), 'a')
        l.tag('a', '//A/D')
        self.assertTagged(os.path.join('A', 'D', 'a'), 'a')

    def test_untag(self):
        l = self.library
        os.chdir('library')
        self.assertTagged(os.path.join('C', 'b'), 'b')
        l.untag('b', '//C')
        self.assertNotTagged(os.path.join('C', 'b'), 'b')

    def test_listtags(self):
        l = self.library
        os.chdir('library')
        self.assertSameTags(l.listtags('a'), ['//'])
        self.assertSameTags(l.listtags('b'), ['//', '//C'])
        l.tag('b', '//A')
        self.assertSameTags(l.listtags('b'), ['//', '//C', '//A'])

    def test_convert(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        p = os.path.join(self.root, l.dirsdir(l.root), 'A')
        self.assertTrue(os.path.isdir(p))
        self.assertEquals(os.readlink('A'), p)
        l.convert('C')
        p = os.path.join(self.root, l.dirsdir(l.root), 'C')
        self.assertTrue(os.path.isdir(p))
        self.assertEquals(os.readlink('C'), p)

    def test_cleandirs(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        l.convert('C')
        l.tag('C', '//A')
        l.tag('C', '//A/D')
        p = os.path.join(self.root, l.dirsdir(l.root), 'C')
        self.assertTrue(os.path.isdir(p))
        os.unlink('C')
        l.cleandirs()
        self.assertTrue(os.path.isdir(p))
        os.unlink('A/C')
        l.cleandirs()
        self.assertTrue(os.path.isdir(p))
        os.unlink('A/D/C')
        l.cleandirs()
        self.assertFalse(os.path.isdir(p))

    def test_find(self):
        l = self.library
        os.chdir('library')
        l.tag('a', '//A/D')
        results = l.find(['//A/D'])
        self.assertEquals(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))
        results = l.find(['//A/D'])
        self.assertEquals(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))
        l.tag('b', '//A/D')
        results = l.find(['//A/D'])
        self.assertEquals(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a', 'b',)))
        l.tag('a', '//B')
        results = l.find(['//A/D', '//B'])
        self.assertEquals(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))

    def test_rm(self):
        l = self.library
        os.chdir('library')
        n = [os.path.join(*x) for x in [
            ['A', 'a'], ['B', 'marisa'], ['A', 'D', 'reimu']
        ]]
        for x in n:
            os.link('a', x)
        n.append('a')
        l.rm('a')
        for x in n:
            self.assertFalse(os.path.exists(x))
