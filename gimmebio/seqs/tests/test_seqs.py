"""Test suite for sample seqs."""

from unittest import TestCase

from gimmebio.seqs import needle_distance, hamming_distance


class TestSeqs(TestCase):
    """Test suite for sample seqs."""

    def test_hamming_dist(self):
        d = hamming_distance('ATCG', 'AACG')
        self.assertAlmostEqual(d, 0.25)

    def test_needle_mismatch(self):
        d = needle_distance('ATCG', 'AACG')
        self.assertAlmostEqual(d, (30 - 5) / 4)

    def test_needle_gap_front(self):
        d = needle_distance('TAACG', 'AACG')
        self.assertAlmostEqual(d, (40 - 6) / 4)

    def test_needle_gap_back(self):
        d = needle_distance('AACG', 'AACGT')
        self.assertAlmostEqual(d, (40 - 6) / 4)

    def test_needle_gap_middle(self):
        d = needle_distance('AACG', 'AATCG')
        self.assertAlmostEqual(d, (40 - 6) / 4)
