"""Test suite for kmer."""

from unittest import TestCase

from gimmebio.kmers import make_kmers


class TestKmers(TestCase):
    """Test suite for wasabi."""

    def test_make_kmers(self):
        """Test that make kmers works."""
        seq = 'ATCGGTA'
        expected_kmers = set(['ATCG', 'TCGA', 'ACCG', 'GGTA'])
        actual_kmers = make_kmers(seq, 4, canon=True)
        for kmer in actual_kmers:
            self.assertIn(kmer, expected_kmers)
