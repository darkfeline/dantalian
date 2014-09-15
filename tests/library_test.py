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

    def test_tag_ok_tag(self):
        l = self.library
        os.chdir('library')
        l.tag('a', '//A')
        self.assertTagged(os.path.join('A', 'a'), 'a')
        l.tag('a', '//A/D')
        self.assertTagged(os.path.join('A', 'D', 'a'), 'a')

    def test_tag_ok_path_rel(self):
        l = self.library
        os.chdir('library')
        l.tag('a', 'B')
        self.assertTagged(os.path.join('B', 'a'), 'a')
        l.tag('a', 'C/')
        self.assertTagged(os.path.join('C', 'a'), 'a')

    def test_tag_ok_path_abs(self):
        l = self.library
        os.chdir('library')
        l.tag('a', os.path.join(self.root, 'library', 'B'))
        self.assertTagged(os.path.join('B', 'a'), 'a')
        l.tag('a', os.path.join(self.root, 'library', 'C/'))
        self.assertTagged(os.path.join('C', 'a'), 'a')

    def test_untag_ok_tag(self):
        l = self.library
        os.chdir('library')
        self.assertTagged(os.path.join('C', 'b'), 'b')
        l.untag('b', '//C')
        self.assertNotTagged(os.path.join('C', 'b'), 'b')

    def test_untag_ok_path_rel(self):
        l = self.library
        os.chdir('library')
        self.assertTagged(os.path.join('C', 'b'), 'b')
        l.untag('b', 'C')
        self.assertNotTagged(os.path.join('C', 'b'), 'b')

    def test_untag_ok_path_rel_trailing(self):
        l = self.library
        os.chdir('library')
        self.assertTagged(os.path.join('C', 'b'), 'b')
        l.untag('b', 'C/')
        self.assertNotTagged(os.path.join('C', 'b'), 'b')

    def test_listtags(self):
        l = self.library
        os.chdir('library')
        self.assertSameTags(l.listtags('a'), ['//'])
        self.assertSameTags(l.listtags('b'), ['//', '//C'])

    def test_convert(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        p = os.path.join(self.root, l.dirsdir, 'A')
        self.assertTrue(os.path.isdir(p))
        self.assertEqual(os.readlink('A'), p)
        l.convert('C')
        p = os.path.join(self.root, l.dirsdir, 'C')
        self.assertTrue(os.path.isdir(p))
        self.assertEqual(os.readlink('C'), p)

    def test_cleandirs(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        l.convert('C')
        l.tag('C', '//A')
        l.tag('C', '//A/D')
        p = os.path.join(self.root, l.dirsdir, 'C')
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
        self.assertEqual(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))
        results = l.find(['//A/D'])
        self.assertEqual(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))
        l.tag('b', '//A/D')
        results = l.find(['//A/D'])
        self.assertEqual(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a', 'b',)))
        l.tag('a', '//B')
        results = l.find(['//A/D', '//B'])
        self.assertEqual(set(results), set(
            os.path.join(l.root, 'A', 'D', x) for x in ('a',)))

    def test_rm(self):
        l = self.library
        os.chdir('library')
        paths = [os.path.join(*x) for x in [
            ['A', 'a'], ['B', 'marisa'], ['A', 'D', 'reimu']
        ]]
        for x in paths:
            os.link('a', x)
        paths.append('a')
        l.rm('a')
        for x in paths:
            self.assertFalse(os.path.exists(x))

    def test_rename(self):
        l = self.library
        os.chdir('library')
        bases = [
            ['A', 'a'], ['B', 'marisa'], ['A', 'D', 'reimu']
        ]
        paths = [os.path.join(*x) for x in bases]
        for x in paths:
            os.link('a', x)
        l.rename('a', 'b')
        bases = [x[:-1] + ['b'] for x in bases]
        paths = [os.path.join(*x) for x in bases]
        self.assertTrue(os.path.exists('b.1'))
        for x in paths:
            self.assertTagged('b.1', x)

    def test_fix(self):
        l = self.library
        os.chdir('library')
        l.convert('A')
        os.chdir(self.root)
        os.rename('library', 'archive')
        l = library.open_library('archive')
        os.chdir('archive')
        l.fix()
        p = os.path.join(self.root, l.dirsdir, 'A')
        self.assertTrue(os.path.isdir(p))
        self.assertEqual(os.readlink('A'), p)
