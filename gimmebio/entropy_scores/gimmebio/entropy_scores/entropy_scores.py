
import pysam
import pandas as pd

from math import log
from Bio import SeqIO

from gimmebio.kmers import make_kmers


def num_unique_subwords(seq, n):
    out = set()
    for kmer in make_kmers(seq, n, canon=False):
        out.add(kmer)
    return len(out)


def seq_entropy_score(seq, n=3):
    sub_seq = seq[0:(4 ** n + n - 1)]
    return log(num_unique_subwords(sub_seq, n), 4) / n


def entropy_score_bam(bam_filename):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    scores = pd.Series([seq_entropy_score(read.query_sequence) for read in samfile])
    return scores.mean()


def entropy_score_fastq(fastq_filename, delim=None):
    fastq = SeqIO.parse(fastq_filename, 'fastq')
    if delim is None:
        scores = pd.Series([seq_entropy_score(read.seq) for read in fastq])
        return [('all', scores.mean())]
    else:
        scores = pd.DataFrame([
            {'genome': read.id.split(delim)[0], 'score': seq_entropy_score(read.seq)}
            for read in fastq
        ])
        scores = scores.groupby('genome').mean()
        return [(genome, row['score']) for genome, row in scores.iterrows()]


def gini_coeff(vals, nvals, min_bins=3):
    vals = sorted(list(vals))
    nbins = max(len(vals), min_bins)
    total_val, total_area = 0, 0
    for val in vals:
        total_val += val
        column = total_val / (nvals * nbins)
        total_area += column
    return total_area


def clump_score(bam_filename, binsize=10000, min_bins=3, delim=None):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    return _clump_score(samfile, binsize=binsize, min_bins=min_bins, delim=delim)


def _clump_score(samfile, binsize=10000, min_bins=3, delim=None):
    bins, nreads = {}, 0
    for read in samfile:
        if read.is_unmapped:
            continue
        nreads += 1
        genome = read.reference_name.split(delim)[0] if delim else 'all'
        if genome not in bins:
            bins[genome] = {}
        pos = read.reference_name, read.reference_start // binsize
        bins[genome][pos] = 1 + bins[genome].get(pos, 0)

    out = []
    for genome, gene_bins in bins.items():
        out.append((genome, gini_coeff(gene_bins.values(), nreads, min_bins=min_bins)))
    return out


def entropy_and_clump_score(bam_filename, binsize=10000, min_bins=3, delim=None):
    samfile = pysam.AlignmentFile(bam_filename, "rb")
    if delim is None:
        escores = pd.Series([seq_entropy_score(read.query_sequence) for read in samfile])
        escore = {'all': escores.mean()}
        cscore = clump_score(bam_filename, binsize=binsize, min_bins=min_bins)
    else:
        escores = pd.DataFrame([
            {'genome': read.reference_name.split(delim)[0], 'score': seq_entropy_score(read.query_sequence)}
            for read in samfile
        ])
        escores = escores.groupby('genome').mean()
        escore = {genome: row['score'] for genome, row in escores.iterrows()}
        cscore = clump_score(bam_filename, binsize=binsize, min_bins=min_bins, delim=delim)

    return escore, cscore
