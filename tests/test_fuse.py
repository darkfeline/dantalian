import unittest
import tempfile
import shutil
import os
import logging
import multiprocessing
import subprocess
import time

from dantalian.library import fs as library

logger = logging.getLogger(__name__)


class TestMount(unittest.TestCase):

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
        r = os.path.join(self.root, 'mnt')
        os.mkdir(r)

    def tearDown(self):

        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def umount(self, path):
        return subprocess.call(['fusermount', '-u', path])

    def test_mount(self):

        l = self.library
        self.proc = MountProcess(l, 'mnt', l.maketree())
        self.proc.start()
        time.sleep(0.5)

        ret = self.umount('mnt')
        self.assertEquals(ret, 0)
        self.proc.join()


class TestFUSE(unittest.TestCase):

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
        r = os.path.join(self.root, 'mnt')
        os.mkdir(r)
        self.fusesock = library.Library.fusesock(r)

        l = self.library
        self.proc = MountProcess(l, 'mnt', l.maketree())
        self.proc.start()
        time.sleep(0.5)

    def tearDown(self):

        self.umount('mnt')
        self.proc.join()

        shutil.rmtree(self.root)
        os.chdir(self._olddir)

    def umount(self, path):
        return subprocess.call(['fusermount', '-u', path])

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

    @unittest.skip('not working')
    def test_mknode(self):
        l = self.library
        with open(self.fusesock, 'w') as f:
            f.write('mknode E //C //B')
            time.sleep(0.5)
        self.assertTrue(os.path.isdir('E'))
        self.assertNotIn('b', os.listdir('E'))
        l.tag('b', '//B')
        self.assertIn('b', os.listdir('E'))


class MountProcess(multiprocessing.Process):

    def __init__(self, lib, path, tree):
        super().__init__()
        self.lib = lib
        self.path = path
        self.tree = tree

    def run(self):
        self.lib.mount(self.path, self.tree)
