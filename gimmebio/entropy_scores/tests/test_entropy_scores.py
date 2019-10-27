"""Test suite for kmer."""

from unittest import TestCase
from os.path import dirname, join

from gimmebio.entropy_scores import (
    entropy_score_bam,
    entropy_score_fastq,
    clump_score,
    entropy_and_clump_score,
)
from gimmebio.sample_seqs import EXAMPLE_FASTQ


BAM_FILE = join(dirname(__file__), 'test_entropy_scores.bam')


class TestEntropyScores(TestCase):
    """Test suite for entropy scores."""

    def test_entropy_scores_bam(self):
        """Test that entropy score works."""
        val = entropy_score_bam(BAM_FILE)
        self.assertTrue(val >= 0)
        self.assertTrue(val <= 1)

    def test_entropy_scores_fastq(self):
        """Test that entropy score works."""
        val = entropy_score_fastq(EXAMPLE_FASTQ)[0][1]
        self.assertTrue(val >= 0)
        self.assertTrue(val <= 1)

    def test_clump_scores(self):
        """Test that clump score works."""
        val = clump_score(BAM_FILE)[0][1]
        self.assertTrue(val >= 0)
        self.assertTrue(val <= 1)

    def test_entropy_scores_fastq_delim(self):
        """Test that entropy score works."""
        val = entropy_score_fastq(EXAMPLE_FASTQ, delim=':')[0][1]
        self.assertTrue(val >= 0)
        self.assertTrue(val <= 1)

    def test_entropy_clump_scores_delim(self):
        """Test that clump score works."""
        escore, cscore = entropy_and_clump_score(BAM_FILE, delim='.')
        self.assertTrue(cscore[0][1] >= 0)
        self.assertTrue(cscore[0][1] <= 1)

