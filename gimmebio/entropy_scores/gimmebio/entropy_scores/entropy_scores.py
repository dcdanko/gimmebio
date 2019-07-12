
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


def clump_score(bam_filename, binsize=10000):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    return _clump_score(samfile, binsize=binsize)


def _clump_score(samfile, binsize=10000):
    nreads, bins = 0, set()
    for read in samfile:
        if read.is_unmapped:
            continue
        nreads += 1
        pos = read.reference_start // binsize
        chrom = read.reference_id
        bins.add((chrom, pos))
    return len(bins) / nreads


def entropy_and_clump_score(bam_filename, binsize=10000):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    escores = pd.Series([seq_entropy_score(read.query_sequence) for read in samfile])
    escore = escores.mean()
    cscore = _clump_score(samfile, binsize=binsize)
    return escore, cscore
