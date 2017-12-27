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
            'gb_highlight_dna=gimmebio.highlight_dna:highlightDNA_CLI',
            'gb_make_kmers=gimmebio.kmers:makeKmers_CLI',
            'gb_make_minsparse_kmers=gimmebio.kmers:makeMinSparseKmers_CLI',            
            'gb_make_alpha_diversity_table=gimmebio.metagenomics.intrasample_diversity:main',
            'gb_process_mpa_files=gimmebio.metagenomics.clip_aggregate_mpa:main',
            'gb_clean_mash_distances=gimmebio.metagenomics.clean_mash_distances:main',
            'gb_aggregate_intersample_distances=gimmebio.metagenomics.aggregate_intersample_diversity:main',
            'gb_aggregate_list=gimmebio.metagenomics.general_aggregate:main',
            'gb_bc_stats=gimmebio.linked_reads.bc_stats:main',            
            'gb_aggregate_abr_tables=gimmebio.metagenomics.abr_table:main',
            'gb_species_tables=gimmebio.metagenomics.species_table:main'            
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
