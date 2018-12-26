#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

setup_requirements = [
    # TODO(dcdanko): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ponce_de_leon',
    version='0.1.0',
    description="Estimate the length of Telomeres",
    long_description=readme + '\n\n' + history,
    author="David Danko",
    author_email='dcdanko@gmail.com',
    url='https://github.com/dcdanko/ponce_de_leon',
    packages=find_packages(include=['ponce_de_leon']),
    entry_points={
        'console_scripts': [
            'leon=ponce_de_leon.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='ponce_de_leon',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
from setuptools import setup

microlib_name = 'gimmebio.kmers'

requirements = [
    'gimmebio.seqs',
]

setup(
    name=microlib_name,
    version='0.2.0',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    namespace_packages=['gimmebio'],
    packages=[microlib_name],
    install_requires=requirements,
)
