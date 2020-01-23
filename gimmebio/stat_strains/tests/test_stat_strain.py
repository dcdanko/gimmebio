"""Test suite for stat strain."""

from unittest import TestCase
import pandas as pd

from os.path import dirname, join, basename

from gimmebio.stat_strains import (
    entropy_reduce_position_matrix,
    entropy_reduce_postion_matrices,
    parallel_entropy_reduce_postion_matrices,
    fast_entropy_reduce_postion_matrices,
)
from gimmebio.stat_strains.metrics import scaling_manhattan

MATRIX_1_FILENAME = join(dirname(__file__), 'NC_006085.1_cds_WP_002515220.1_751.counts.txt.gz')
MATRIX_2_FILENAME = join(dirname(__file__), 'NC_006085.1_cds_WP_002516475.1_2279.counts.txt.gz')
MATRIX_3_FILENAME = join(dirname(__file__), 'NC_006085.1_cds_WP_002515415.1_1951.counts.txt.gz')
ONE_COL_FILENAME = join(dirname(__file__), 'count_matrix_with_one_col.csv')
NULL_FILENAME = join(dirname(__file__), 'null_count_matrix.csv')


def _parse_matrix(filehandle):
    matrix = pd.read_csv(filehandle, index_col=0, header=0)
    pref = basename(filehandle) + '__'
    matrix.columns = [pref + el for el in matrix.columns]
    return matrix


def trivial_metric(x, y):
    return 0.


class TestStatStrain(TestCase):
    """Test suite for ram seq."""

    def test_trivial_reduce_entropy_full_reduce(self):
        """Test that we only get 1 column."""
        original = pd.read_csv(MATRIX_1_FILENAME, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            original,
            1,
            trivial_metric
        )
        self.assertEqual(full_reduced.shape[0], original.shape[0])
        self.assertEqual(full_reduced.shape[1], 1)

    def test_reduce_entropy_reduce(self):
        """Test that we only get 1 column."""
        original = pd.read_csv(MATRIX_1_FILENAME, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            original,
            0.1,
            'cosine'
        )
        self.assertEqual(full_reduced.shape[0], original.shape[0])
        self.assertLess(full_reduced.shape[1], original.shape[1])

    def test_reduce_entropy_reduce_2(self):
        """Test that we only get 1 column."""
        original = pd.read_csv(MATRIX_3_FILENAME, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            original,
            0.1,
            'cosine'
        )
        self.assertEqual(full_reduced.shape[0], original.shape[0])
        self.assertLess(full_reduced.shape[1], original.shape[1])

    def test_reduce_two_matrices_trivial_full_reduce(self):

        def _parse_matrix(filehandle):
            matrix = pd.read_csv(filehandle, index_col=0, header=0)
            pref = basename(filehandle) + '__'
            matrix.columns = [pref + el for el in matrix.columns]
            return matrix

        full_reduced = entropy_reduce_postion_matrices(
            [MATRIX_1_FILENAME, MATRIX_2_FILENAME],
            1,
            trivial_metric,
            matrix_parser=_parse_matrix
        )
        self.assertEqual(full_reduced.shape[1], 1)

    def _test_parallel_reduce_two_matrices_trivial_full_reduce(self):
        full_reduced = parallel_entropy_reduce_postion_matrices(
            [MATRIX_1_FILENAME, MATRIX_2_FILENAME],
            1,
            trivial_metric,
            matrix_parser=_parse_matrix,
            threads=4,
        )
        self.assertEqual(full_reduced.shape[1], 1920)

    def test_fast_reduce_two_matrices_trivial_full_reduce(self):
        full_reduced = fast_entropy_reduce_postion_matrices(
            [MATRIX_1_FILENAME, MATRIX_2_FILENAME],
            1,
            trivial_metric,
            matrix_parser=_parse_matrix,
        )
        self.assertEqual(full_reduced.shape[1], 1920)

    def test_reduce_null_matrix_is_empty(self):
        """Test that we only get 1 column."""
        original = pd.read_csv(NULL_FILENAME, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            original,
            1,
            trivial_metric
        )
        self.assertEqual(full_reduced.shape[0], original.shape[0])
        self.assertEqual(full_reduced.shape[1], 0)

    def test_fast_reduce_first_matrix_one_col(self):
        full_reduced = fast_entropy_reduce_postion_matrices(
            [ONE_COL_FILENAME, MATRIX_1_FILENAME, MATRIX_2_FILENAME],
            0.1,
            'cosine',
            matrix_parser=_parse_matrix,
        )
        self.assertGreater(full_reduced.shape[1], 1)

    def test_fast_reduce_first_matrix_null(self):
        full_reduced = fast_entropy_reduce_postion_matrices(
            [NULL_FILENAME, ONE_COL_FILENAME, MATRIX_1_FILENAME, MATRIX_2_FILENAME],
            0.1,
            'cosine',
            matrix_parser=_parse_matrix,
        )
        self.assertGreater(full_reduced.shape[1], 1)

    def test_fast_reduce_with_matrix_null(self):
        full_reduced = fast_entropy_reduce_postion_matrices(
            [MATRIX_1_FILENAME, NULL_FILENAME, MATRIX_2_FILENAME],
            0.1,
            'cosine',
            matrix_parser=_parse_matrix,
        )
        self.assertGreater(full_reduced.shape[1], 1)
