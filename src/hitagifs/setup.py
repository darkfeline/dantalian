#!/usr/bin/env python

from distutils.core import setup

setup(
    name='hitagifs',
    version='0,1',
    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    url='http://abagofapples.com/',
    package_dir={'': 'src'},
    packages=['hitagifs'],
    modules=['fuse3'],
    scripts=['src/bin/torrent-preview'],
)
