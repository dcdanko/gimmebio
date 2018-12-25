import setuptools

setuptools.setup(
    name="taxa_ags_normalizer",
    version="0.9.0",
    url="https://github.com/dcdanko/taxa_ags_normalizer",

    author="David C. Danko",
    author_email="dcdanko@gmail.com",

    description="Normalize Taxonomic Profiles By Average Genome Size",
    long_description=open('README.rst').read(),

    packages=['taxon_normalizer'],
    package_dir={'taxon_normalizer': 'taxon_normalizer'},

    install_requires=[
        'click==6.7'
    ],

    entry_points={
        'console_scripts': [
            'taxon_normalizer=taxon_normalizer.cli:main'
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
