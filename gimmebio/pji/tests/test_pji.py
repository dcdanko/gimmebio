"""Test suite for pji."""

from unittest import TestCase
from os.path import dirname, join
import pandas as pd

from gimmebio.pji import identify_pji_taxa


TAXA_FILE = join(dirname(__file__), 'refseq.krakenhll_longform.csv.gz')


class TestPJI(TestCase):
    """Test suite for PJI."""

    def test_identify_pji_taxa(self):
        longtaxa = pd.read_csv(TAXA_FILE, compression='gzip')
        longtaxa.columns = [
            'sample_name', 'taxa_name', 'taxa_id', 'rank', 'mpa',
            'cov', 'dup', 'kmers', 'percent', 'reads', 'tax_reads'
        ]
        longtaxa = longtaxa.query('kmers > 256')
        identified = identify_pji_taxa(longtaxa)
        print(identified)
