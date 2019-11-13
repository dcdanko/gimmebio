from setuptools import setup

microlib_name = 'gimmebio.kmers'

requirements = [
    'gimmebio.seqs',
    'gimmebio.ram_seq'
]

setup(
    name=microlib_name,
    version='0.4.8',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    namespace_packages=['gimmebio'],
    packages=[microlib_name, microlib_name + '.clustering'],
    install_requires=requirements,
)
