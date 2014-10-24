from setuptools import setup, find_packages

setup(
    name='dantalian',
    version='0.5',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    entry_points={
        'console_scripts': [
            'dantalian = dantalian.main:main',
        ],
    },
    test_suite="tests",

    author='Allen Li',
    author_email='darkfeline@abagofapples.com',
    description='',
    license='MIT',
    url='http://darkfeline.github.io/dantalian/',
)
