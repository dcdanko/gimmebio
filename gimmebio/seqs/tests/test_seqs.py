"""Test suite for sample seqs."""

from unittest import TestCase
from os.path import dirname, join

from gimmebio.seqs import needle_distance, hamming_distance
from gimmebio.seqs.concat_lanes import (
    group_filenames_by_sep,
    group_filenames_by_name_read_lane,
    concatenate_grouped_filenames,
)


class TestSeqs(TestCase):
    """Test suite for sample seqs."""

    def test_hamming_dist(self):
        d = hamming_distance('ATCG', 'AACG')
        self.assertAlmostEqual(d, 0.25)

    def test_needle_mismatch(self):
        d = needle_distance('ATCG', 'AACG')
        self.assertAlmostEqual(d, -(3 - .5) / 4)

    def test_needle_gap_front(self):
        d = needle_distance('TAACG', 'AACG')
        self.assertAlmostEqual(d, -(4 - .6) / 4)

    def test_needle_gap_back(self):
        d = needle_distance('AACG', 'AACGT')
        self.assertAlmostEqual(d, -(4 - .6) / 4)

    def test_needle_gap_middle(self):
        d = needle_distance('AACG', 'AATCG')
        self.assertAlmostEqual(d, -(4 - .6) / 4)

    def test_concat_lanes(self):
        fnames = open(join(dirname(__file__), 'fnames.txt')).read().split('\n')
        grouped = group_filenames_by_name_read_lane(fnames)
        concatenate_grouped_filenames(grouped, dryrun=True, dest_dir='.')
