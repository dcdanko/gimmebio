from setuptools import setup, find_packages
from codecs import open as codex_open
from os import path

__version__ = '0.0.1'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codex_open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with codex_open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='operonator',
    version=__version__,
    description='Find operons in metagenomic linked read data.',
    long_description=long_description,
    url='https://github.com/dcdanko/operonator',
    download_url='https://github.com/dcdanko/operonator/tarball/' + __version__,
    license='BSD',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='David Danko',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='dcdanko@gmail.com',
    entry_points={
        'console_scripts': [
            'operonator=operonator.cli:main'
        ]
    },
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
