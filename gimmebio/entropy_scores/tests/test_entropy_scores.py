"""Test suite for kmer."""

from unittest import TestCase
from os.path import dirname, join

from gimmebio.entropy_scores import entropy_score


BAM_FILE = join(dirname(__file__), 'test_entropy_scores.bam')


class TestEntropyScores(TestCase):
    """Test suite for entropy scores."""

    def test_entropy_scores(self):
        """Test that make kmers works."""
        val = entropy_score(BAM_FILE)
        self.assertTrue(val >= 0)
        self.assertTrue(val <= 1)
