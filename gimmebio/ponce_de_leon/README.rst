=============
Ponce De Leon
=============


.. image:: https://img.shields.io/pypi/v/ponce_de_leon.svg
        :target: https://pypi.python.org/pypi/ponce_de_leon

.. image:: https://img.shields.io/travis/dcdanko/ponce_de_leon.svg
        :target: https://travis-ci.org/dcdanko/ponce_de_leon

.. image:: https://readthedocs.org/projects/ponce-de-leon/badge/?version=latest
        :target: https://ponce-de-leon.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/dcdanko/ponce_de_leon/shield.svg
     :target: https://pyup.io/repos/github/dcdanko/ponce_de_leon/
     :alt: Updates


Estimate the length of Telomeres


* Free software: MIT license
* Documentation: https://ponce-de-leon.readthedocs.io.

Installation
------------

.. code-block:: bash

   $ python setup.py develop
   $ python setup.py test

  
Tools
-----

Leon provides a set of tools for manipulating linked reads

Filter bcs, given a list of regions and a sam file produce a list of barcodes where at least one read has one alignment within one region.

.. code-block:: bash

    $ leon filter bc-by-region <bed file> <fastq file> <sam file> > bc_list.txt
    $ samtools view <sam file> | leon filter-bcs <bed file> <fastq file> > bc_list.txt


Filter reads, given a list of barcodes only return reads with those barcodes.

.. code-block:: bash

    $ leon filter read-by-bc <bc list> <fastq> > reads_with_bc.fq
    $ cat <fastq> | leon filter read-by-bc <bc list> > reads_with_bc.fq

    
Filter records in a SAM file with barcodes.
    
.. code-block:: bash

    $ leon filter sam-by-bc <bc list> <sam file> > reads_with_bc.sam
    $ cat <sam file> | leon filter sam-by-bc <bc list> > reads_with_bc.sam

    
Identify Kmers, given a fastq file return a list of 'high abundance' kmers. 
 - kmers should all be within a specified min and max length
 - kmers that are equivalent (rotation and reverse complement) should be grouped
 - include canonical kmer
 - include frequency and total count of all kmer groups

.. code-block:: bash

    $ leon kmerize <fastq> > kmer_list.csv
    $ cat <fastq> | leon kmerize > kmer_list.csv
    $ cat kmer_list.csv
    ,total,frequency,k,sequences
    ATC,10,0.1,3,ATC TCA CAT GAT TGA ATG
    `...`





Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

