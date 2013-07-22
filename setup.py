#!/usr/bin/env python

from distutils.core import setup

setup(
    name='dantalian',
    version='0.4.1',
    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    url='http://abagofapples.com/',
    package_dir={'': 'src'},
    packages=['dantalian'],
    scripts=['src/bin/dantalian'],
)
