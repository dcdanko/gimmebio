from setuptools import setup

microlib_name = 'gimmebio.cli'

requirements = [
    'scipy',
    'numpy',
    'pandas',
    'click',
]

setup(
    name=microlib_name,
    version='0.1.5',
    author='David Danko',
    author_email='dcdanko@gmail.com',
    license='MIT license',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'gimmebio=gimmebio.cli.cli:main'
        ]
    },
    namespace_packages=['gimmebio'],
    packages=[microlib_name],
    install_requires=requirements,
)
