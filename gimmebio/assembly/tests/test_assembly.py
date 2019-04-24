"""Test suite for linked reads."""

from unittest import TestCase

from gimmebio.assembly import (
    assign_contigs,
    compress_assigned_contigs,
    condense_winner_takes_all,
)
from os.path import join, dirname, abspath


TEST_DIR = abspath(dirname(__file__))
M8_FILE = join(TEST_DIR, 'sample_m8.m8')
FASTA_FILE = join(TEST_DIR, 'sample_fasta.fa')
GENBANK_ABBREV = join(TEST_DIR, 'genbank_sample.tsv.gz')


# # Generate a table for manual inspection
# with open(M8_FILE) as m8f, open(FASTA_FILE) as faf:
#     tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV, seqfile=faf)
#     tbl = compress_assigned_contigs(tbl, min_cov=0, max_cov=10, rank='phylum')
#     print(tbl)


class TestAssembly(TestCase):
    """Test suite for assembly."""

    def test_contig_assignment(self):
        with open(M8_FILE) as m8f:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV)
        self.assertEqual(tbl.shape[0], 3)
        self.assertEqual(tbl.shape[1], 4)

    def test_contig_assignment_with_fasta(self):
        with open(M8_FILE) as m8f, open(FASTA_FILE) as faf:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV, seqfile=faf)
        self.assertEqual(tbl.shape[0], 3)
        self.assertEqual(tbl.shape[1], 6)

    def test_condense_ids(self):
        with open(M8_FILE) as m8f, open(FASTA_FILE) as faf:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV, seqfile=faf)
        tbl = compress_assigned_contigs(tbl, min_cov=0, max_cov=10)
        self.assertEqual(tbl.shape[0], 3)

    def test_condense_ids_wta(self):
        with open(M8_FILE) as m8f, open(FASTA_FILE) as faf:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV, seqfile=faf)
        tbl = compress_assigned_contigs(tbl, min_cov=0, max_cov=10)
        tbl = condense_winner_takes_all(tbl)
        self.assertEqual(tbl.shape[0], 3)

    def test_condense_ids_rank(self):
        with open(M8_FILE) as m8f, open(FASTA_FILE) as faf:
            tbl = assign_contigs(m8f, genfile=GENBANK_ABBREV, seqfile=faf)
        tbl = compress_assigned_contigs(tbl, rank='phylum', min_cov=0, max_cov=10)
        self.assertEqual(tbl.shape[0], 2)
