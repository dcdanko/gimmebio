"""Test suite for kmer."""

from unittest import TestCase


from gimmebio.sample_seqs import EcoliGenome

from gimmebio.kmers import make_kmers
from gimmebio.kmers.clustering import GreedyRadialCover, hamming_distance

ECOLI = EcoliGenome()


class TestKmerClustering(TestCase):
    """Test suite for wasabi."""

    def test_make_kmers(self):
        """Idiot check myself."""
        make_kmers(ECOLI.longest_contig()[:1000], 31, canon=True)

    def test_init_cover(self):
        GreedyRadialCover(hamming_distance, 2)

    def test_add_to_cover(self):
        kmers = make_kmers(ECOLI.longest_contig()[:1000], 31, canon=True)
        radial_cover = GreedyRadialCover(hamming_distance, 2)
        for kmer in kmers:
            radial_cover.add(kmer)

    def test_kmer_stats(self):
        kmers = make_kmers(ECOLI.longest_contig()[:1000], 31, canon=True)
        radial_cover = GreedyRadialCover(hamming_distance, 2)
        for kmer in kmers:
            radial_cover.add(kmer)
        radial_cover.stats()
        for kmer in kmers[:10]:
            radial_cover.search(kmer, 1)
