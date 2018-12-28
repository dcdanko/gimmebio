gimmebio
========

.. image:: https://img.shields.io/pypi/v/gimmebio.svg
        :target: https://pypi.python.org/pypi/gimmebio

.. image:: https://circleci.com/gh/dcdanko/gimmebio.svg?style=svg
    :target: https://circleci.com/gh/dcdanko/gimmebio

.. image:: https://www.codefactor.io/Content/badges/A.svg
    :target: https://www.codefactor.io/repository/github/dcdanko/gimmebio

Utilities and explorations in computational Biology. MIT License.

Packages
--------

- Kmers, make kmers of many different styles.
- Linked Reads, utilities for handling linked read data
- Seqs, general utilites for handling sequence data. Some IO which should be deprecated
- Bayesian First Aid, incomplete python implementation of bfa_
- Hiveplots, python implemnetation of hiveplots with area hiveplots
- operonator, experiment using linked reads to detect gene clusters
- ponce_de_leon, experiment using Approx Bayesian Computation to bridge low complexity regiosn
- ram_seq, use Ramanujan-Fourier transform to process sequence data
- seqtalk, experiment with neural nets for sequence processing
- taxa_ags_normalizer, estimate average genome size for taxa

Installation
------------

Install from source.

.. code-block:: bash

    git clone git@github.com:dcdanko/gimmebio.git
    cd gimmebio
    python setup.py install


Credits
-------


This package is structured as a set of microlibraries_

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

`gimmebio` was written by `David C. Danko <dcdanko@gmail.com>`_.

.. _bfa: https://github.com/rasmusab/bayesian_first_aid
.. _metadata: https://github.com/MetaSUB/MetaSUB-metadata
.. _metagenscope: https://www.metagenscope.com/
.. _microlibraries: https://blog.shazam.com/python-microlibs-5be9461ad979
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _AWS-CLI: https://docs.aws.amazon.com/cli/latest/userguide/installing.html

