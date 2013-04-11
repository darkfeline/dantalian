"""
setcache.py
===========

Sets, and caching.  Uses str/tuples for terms and sets for contents
"""

from collections import defaultdict
from collections import namedtuple

__all__ = ['SetCache', 'Unit']
Unit = namedtuple('Unit', ['contents', 'unions', 'intersections'])


def make_unit(contents):
    return Unit(contents, dict(), dict())


class SetCache:

    """
    Attributes:

    units
        {str: Unit}
    unions
    intersections
        {Unit: {Unit: Unit}}

    Methods:

    __init__
    add_unit
    get
    union
    intersect
    insert
    delete
    """

    AND = 'AND'
    OR = 'OR'

    def __init__(self):
        self.units = {}
        self.unions = defaultdict(dict)
        self.intersections = defaultdict(dict)

    def add_unit(self, name, contents):
        assert isinstance(name, str)
        assert isinstance(contents, set)
        self.units[name] = make_unit(contents)

    def _add_union(self, a, b, c):
        assert isinstance(a, Unit)
        assert isinstance(b, Unit)
        assert isinstance(c, set)
        c = make_unit(c)
        a.unions[b] = c
        b.unions[a] = c
        self.unions[a][b] = c
        self.unions[b][a] = c

    def _add_intersection(self, a, b, c):
        assert isinstance(a, Unit)
        assert isinstance(b, Unit)
        assert isinstance(c, set)
        c = make_unit(c)
        a.intersections[b] = c
        b.intersections[a] = c
        self.intersections[a][b] = c
        self.intersections[b][a] = c

    def get(self, unit):
        a, op, b = unit
        if isinstance(a, str):
            a = self.units[a]
        if isinstance(b, str):
            b = self.units[b]
        ops = {self.AND: self.intersect, self.OR: self.union}
        return ops[op](a, b)

    def union(self, a, b):
        try:
            return self.unions[a][b]
        except KeyError:
            result = a | b
            self._add_union(a, b, result)
            return result

    def intersect(self, a, b):
        try:
            return self.intersections[a][b]
        except KeyError:
            result = a & b
            self._add_intersection(a, b, result)
            return result

    def insert(self, name, item):
        try:
            unit = self.units[name]
        except KeyError:
            pass
        else:
            self._insert(unit, item)

    def _insert(self, unit, item):
        if item in unit.contents:
            return
        unit.contents.add(item)
        for b, x in unit.unions.items():
            self.insert(x, item)
        for b, x in unit.intersections.items():
            if item in b:
                self._insert(x, item)

    def delete(self, name, item):
        try:
            unit = self.units[name]
        except KeyError:
            pass
        else:
            self._delete(unit, item)

    def _delete(self, unit, item):
        if item not in unit.contents:
            return
        unit.contents.remove(item)
        for b, x in unit.unions.items():
            if x not in b:
                self._delete(x, item)
        for b, x in unit.intersections.items():
            self.delete(x, item)
