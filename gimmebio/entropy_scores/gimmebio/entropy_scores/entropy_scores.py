
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
    scores = pd.Series([seq_entropy_score(read.seq) for read in samfile])
    return scores.mean()
