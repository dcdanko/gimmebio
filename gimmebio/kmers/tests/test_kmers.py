"""Test suite for kmer."""

from unittest import TestCase

from gimmebio.kmers import make_kmers


class TestKmers(TestCase):
    """Test suite for wasabi."""

    def test_make_kmers(self):
        """Test that make kmers works."""
        seq = 'ATCGGTA'
        expected_kmers = set(['ATCG', 'TCGG', 'CGGT', 'GGTA'])
        actual_kmers = make_kmers(seq, 4, canon=False)
        for kmer in actual_kmers:
            self.assertIn(kmer, expected_kmers)

    def test_make_canon_kmers(self):
        """Test that make kmers works."""
        seq = 'ATCGGTA'
        expected_kmers = set(['ATCG', 'CCGA', 'ACCG', 'GGTA'])
        actual_kmers = make_kmers(seq, 4, canon=True)
        for kmer in actual_kmers:
            self.assertIn(kmer, expected_kmers)
