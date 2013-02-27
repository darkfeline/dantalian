#!/usr/bin/env python

from distutils.core import setup

setup(
    name='dantalian',
    version='0.3',
    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    url='http://abagofapples.com/',
    package_dir={'': 'src'},
    packages=['dantalian', 'dantalian.library'],
    scripts=['src/bin/dantalian'],
)
