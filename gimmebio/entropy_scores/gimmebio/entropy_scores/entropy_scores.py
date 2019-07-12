
import pysam
import pandas as pd

from math import log
from gimmebio.kmers import make_kmers


def num_unique_subwords(seq, n):
    out = set()
    for kmer in make_kmers(seq, n, canon=False):
        out.add(kmer)
    return len(out)


def seq_entropy_score(seq, n=3):
    sub_seq = seq[0:(4 ** n + n - 1)]
    return log(num_unique_subwords(sub_seq, n), 4) / n


def entropy_score(bam_filename):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    scores = pd.Series([seq_entropy_score(read.query_sequence) for read in samfile])
    return scores.mean()


def gini_coeff(vals, nvals):
    vals = sorted(list(vals))
    total_val, total_area = 0, 0
    for val in vals:
        total_val += val
        column = total_val / (nvals * len(vals))
        total_area += column
    return total_area / 0.5


def clump_score(bam_filename, binsize=10000):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    return _clump_score(samfile, binsize=binsize)


def _clump_score(samfile, binsize=10000):
    bins, nreads = {}, 0
    for read in samfile:
        if read.is_unmapped:
            continue
        nreads += 1
        pos = read.reference_id, read.reference_start // binsize
        bins[pos] = 1 + bins.get(pos, 0)
    return gini_coeff(bins.values(), nreads)


def entropy_and_clump_score(bam_filename, binsize=10000):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    escores = pd.Series([seq_entropy_score(read.query_sequence) for read in samfile])
    escore = escores.mean()
    cscore = _clump_score(samfile, binsize=binsize)
    return escore, cscore
