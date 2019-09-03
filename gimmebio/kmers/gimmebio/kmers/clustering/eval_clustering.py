from time import clock
import pandas as pd
from random import shuffle

from .radial_cover import GreedyRadialCover
from .kd_rft_cover import KDRFTCover


def hamming_distance(k1, k2):
    d = 0
    for v1, v2 in zip(k1, k2):
        d += 1 if v1 != v2 else 0
    return d


def radial_cover_cluster(kmer_generator):
    """Build and eval radial clusters over kmers."""
    search_set = [kmer_generator() for _ in range(100)]
    radial_cover = GreedyRadialCover(hamming_distance, 3)
    tbl = []
    for N in [1000, 10 * 1000, 100 * 1000, 500 * 1000]:
        for kmer in [kmer_generator() for _ in range(N)]:
            radial_cover.add(kmer)
        stats = radial_cover.stats()

        start = clock()
        for kmer in search_set:
            radial_cover.search(kmer, 2)
        stats['search_time'] = clock() - start
        tbl.append(stats)

    return pd.DataFrame(tbl)


def eval_kd_cluster(kmers):
    """Build and eval radial clusters over kmers."""
    shuffle(kmers)
    search_set, kmers = kmers[:1000], kmers[1000:]
    for H in [0.15, 0.125, 0.1, 0.075, 0.05]:
        kdrft_cover = KDRFTCover(H)

        start = clock()
        for kmer in kmers:
            kdrft_cover.add(kmer)
        kdrft_cover.greedy_clusters()
        build_time = clock() - start

        stats = kdrft_cover.stats()
        stats['build_time'] = build_time
        stats['H'] = H

        start = clock()
        for kmer in search_set:
            kdrft_cover.search(kmer, 2)
        stats['search_time'] = (clock() - start)
        yield stats


