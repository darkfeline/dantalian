#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='dantalian',
    version='0.5',
    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    url='http://abagofapples.com/',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=['src/bin/dantalian'],
)
