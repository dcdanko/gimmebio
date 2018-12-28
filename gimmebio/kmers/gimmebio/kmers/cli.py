"""CLI for kmer related stuff."""

import click
import sys

from .kmers import make_kmers
from .min_sparse_kmers import MinSparseKmerSet


@click.group()
def kmers():
    """Utilities for kmers."""
    pass


@kmers.command('standard')
@click.option('-k', '--kmer-len', default=32, help='Length of kmers')
@click.option('--canonical/--non-canonical', default=False, help='Canonicalize kmers')
def make_kmers_CLI(kmer_len, canonical):
    for line in sys.stdin:
        seq = line.strip()
        kmers = make_kmers(seq, kmer_len, canon=canonical)
        for kmer in kmers:
            print(kmer)


@kmers.command('minsparse')
@click.option('-k', '--kmer-len', default=20, help='Length of kmers')
@click.option('-w', '--window-len', default=40, help='Length of window, in bases')
def makeMinSparseKmers_CLI(kmer_len, window_len):
    for line in sys.stdin:
        seq = line.strip()
        kmers = MinSparseKmerSet(kmer_len, window_len, [seq])
        for i, kmer in enumerate(kmers):
            if i == 0:
                sys.stdout.write(kmer)
            else:
                sys.stdout.write('\t{}'.format(kmer))
        sys.stdout.write('\n')


if __name__ == '__main__':
    kmers()
