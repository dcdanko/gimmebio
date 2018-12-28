"""Test suite for ram seq."""

from unittest import TestCase
import numpy as np

from gimmebio.ram_seq import rs_matrix, seq_to_matrix


class TestRamSeq(TestCase):
    """Test suite for ram seq."""

    def test_fibbonaci(self):
        """Test that we get the correct values for ram sum of fibbonacci."""
        fibs = np.array([1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
        RS = rs_matrix(len(fibs))
        observed = np.dot(RS, fibs).tolist()[0]
        expected = [14.3, 3.3, -0.55, -4.0, 3.925, -5.85, -0.86666667, 1.8, 2.9, 5.425]
        self.assertEqual(len(observed), len(expected))
        for i in range(len(observed)):
            self.assertAlmostEqual(observed[i], expected[i])

    def test_seq_to_matrix(self):
        """Check that we correctly convert a seq to a matrix."""
        expected = np.matrix([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])
        observed = seq_to_matrix('ACACGTGT')
        self.assertTrue((expected == observed).all())
