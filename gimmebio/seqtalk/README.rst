DataSuper
=========

.. image:: https://img.shields.io/pypi/v/DataSuper.svg
    :target: https://pypi.python.org/pypi/DataSuper
    :alt: Latest PyPI version

Easy to use pipelines for large biological datasets.

Goals
-----

Bioinformatics pipelines often involve a large number of files with complex organization and metadata. Often researchers keep these files organized with carefully patterned filenames, elaborate directory structures and spreadsheets containing metadata. 

DataSuper builds on this approach. DataSuper provides a system to track files that groups files into related modules (i.e. the two fastq files usually used to represent forward and reverse reads), groups sets of modules with samples that store metadata, and groups sets of samples into projects. All of this information is stored in a simple yet customizable database with an API for programmatic access.

DataSuper is probably overkill for small projects, it has been designed in particular for the MetaSUB project which has thousands of samples and complex analysis pipelines. DataSuper makes it easier to keep track of the huge number of files associated with the analysis of these samples, in particular it helps as a bottom layer that can be accessed by higher level applications. 

MetaSUB is also developing a program called ModuleUltra which builds off DataSuper and SnakeMake to provide easily distributable versioned pipelines.

In summary:
 - DataSuper works without disrupting existing bioinformatic workflows
 - DataSuper tightly packages data with metadata
 - DataSuper groups files in the same project
 - DataSuper packages data that is stored across multiple files
 - DataSuper allows programmatic access and ad-hoc grouping of files

Eventually DataSuper will support peer-to-peer sharing so that data can be more easily shared across academic sites.

Installation
------------

Be aware that DataSuper is still an Alpha. There are likely many bugs, fotunately there is no risk that DataSuper will delete your files since it only exists as a layer on top of your systems filesystem.

DataSuper is currently being used on Ubuntu and RHEL systems. It should work on any *nix system.

To install:


.. code-block:: bash
   
    git clone <url>   

    python setup.py develop


Licence
-------
MIT License

Authors
-------

`DataSuper` was written by `David C. Danko <dcdanko@gmail.com>`_.
