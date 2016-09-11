from setuptools import setup, find_packages

setup(
    name='dantalian',
    version='1.0.0',
    description='File tagging with hard links',
    long_description='',
    keywords='',
    url='http://darkfeline.github.io/dantalian/',
    author='Allen Li',
    author_email='darkfeline@felesatra.moe',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3.5',
    ],

    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'dantalian = dantalian.main:main',
        ],
    },
)
