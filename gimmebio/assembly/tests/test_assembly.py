"""Test suite for linked reads."""

from unittest import TestCase

from gimmebio.assembly import assign_contigs
from os.path import join, dirname, abspath


TEST_DIR = abspath(dirname(__file__))
M8_FILE = join(TEST_DIR, 'sample_m8.m8')
GENBANK_ABBREV = join(TEST_DIR, 'genbank_sample.tsv.gz')
print(GENBANK_ABBREV)


class TestAssembly(TestCase):
    """Test suite for assembly."""

    def test_contig_assignment(self):
        with open(M8_FILE) as m8f:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV)
        self.assertTrue(tbl.shape[0])
