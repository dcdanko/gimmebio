import setuptools

setuptools.setup(
    name="SeqTalk",
    version="0.9.0",
    url="https://github.com/dcdanko/SeqTalk",

    author="David C. Danko",
    author_email="dcdanko@gmail.com",

    description="",

    packages=['datasuper'],
    package_dir={'datasuper': 'datasuper'},

    install_requires=[],

    entry_points={
        'console_scripts': [
            'datasuper=datasuper.cli:main'
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
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
