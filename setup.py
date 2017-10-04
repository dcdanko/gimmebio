import setuptools

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]


setuptools.setup(
    name="gimmebio",
    version="0.1.0",
    url="https://github.com/dcdanko/gimmebio.git",

    author="David C. Danko",
    author_email="dcdanko@gmail.com",

    description="Common functions for comp. bio",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    ext_modules = [setuptools.Extension("cseqs", ["cext_gimmebio/_cseqs.c","cext_gimmebio/cseqs.c"])],

    entry_points= {
        'console_scripts': [
            'highlight_dna=gimmebio.highlight_dna:highlightDNA_CLI',
            'make_kmers=gimmebio.kmers:makeKmers_CLI',
            'make_alpha_diversity_table=gimmebio.metagenomics.intrasample_diversity:main'
            ]
        },
    
    install_requires=requirements,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
