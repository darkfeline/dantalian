# Copyright (C) 2015  Allen Li
#
# This file is part of Dantalian.
#
# Dantalian is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dantalian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dantalian.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains unit tests for dantalian.library.taglib
"""

import os
import posixpath
from unittest import TestCase

from dantalian.library import taglib

from . import testlib

# pylint: disable=missing-docstring


class TestLibraryTags(TestCase):

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


class TestLibraryRoot(testlib.FSMixin):

    def setUp(self):
        super().setUp()
        os.makedirs('A/.dantalian')
        os.mknod('A/.dantalian/foo')
        os.makedirs('A/foo/bar')
        os.makedirs('B/foo/bar')

    def test_is_library(self):
        self.assertTrue(taglib.is_library('A'))
        self.assertFalse(taglib.is_library('B'))

    def test_find_library(self):
        self.assertEqual(taglib.find_library('A/foo/bar'), posixpath.abspath('A'))

    def test_init_library(self):
        taglib.init_library('B')
        self.assertTrue(taglib.is_library('B'))

    def test_get_resource(self):
        self.assertEqual(taglib.get_resource('A', 'foo'), 'A/.dantalian/foo')
