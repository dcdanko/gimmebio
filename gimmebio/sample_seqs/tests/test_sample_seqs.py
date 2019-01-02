"""Test suite for sample seqs."""

from unittest import TestCase

from gimmebio.sample_seqs import EcoliGenome


class TestSampleSeqs(TestCase):
    """Test suite for sample seqs."""

    def test_ecoli(self):
        """Test that we get a histogram with the correct number of lines."""
        ecoli = EcoliGenome
        self.assertTrue(len(ecoli.longest_contig()) > 4 * 1000 * 1000)
