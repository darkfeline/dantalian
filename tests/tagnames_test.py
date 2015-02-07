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
This module contains unit tests for dantalian.tagnames
"""

from unittest import TestCase

from dantalian import tagnames

# pylint: disable=missing-docstring


class TestTagnames(TestCase):

    def test_is_tag(self):
        self.assertTrue(tagnames.is_tag('//foo/tag'))
        self.assertTrue(tagnames.is_tag('/////foo/tag'))
        self.assertFalse(tagnames.is_tag('/foo/tag'))
        self.assertFalse(tagnames.is_tag('foo/tag'))

    def test_path2tag(self):
        self.assertEqual(tagnames.path2tag('/foo', '/foo/bar'), '//bar')

    def test_tag2path(self):
        self.assertEqual(tagnames.tag2path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(tagnames.tag2path('/foo', '///bar'), '/foo/bar')

    def test_path(self):
        self.assertEqual(tagnames.path('/foo', '//bar'), '/foo/bar')
        self.assertEqual(tagnames.path('/foo', '/bar'), '/bar')

    def test_tag(self):
        self.assertEqual(tagnames.tag('/foo', '//bar'), '//bar')
        self.assertEqual(tagnames.tag('/foo', '/foo/bar'), '//bar')
