"""Test suite for stat strain."""

from unittest import TestCase
import pandas as pd

from os.path import dirname, join

from gimmebio.stat_strains import entropy_reduce_position_matrix

MATRIX_FILENAME = join(dirname(__file__), 'NC_006085.1_cds_WP_002518620.1_124.counts.csv.gz')


class TestRamSeq(TestCase):
    """Test suite for ram seq."""

    def test_trivial_reduce_entropy_full_reduce(self):
        """Test that we only get 1 column."""
        original = pd.read_csv(MATRIX_FILENAME, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            original,
            1,
            lambda x, y: 0.
        )
        self.assertEqual(full_reduced.shape[0], original.shape[0])
        self.assertEqual(full_reduced.shape[1], 1)
