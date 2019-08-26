from setuptools import setup

microlib_name = 'gimmebio.entropy_scores'

requirements = [
    'pandas',
    'pysam',
]

setup(
    name=microlib_name,
    version='0.4.2',
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
