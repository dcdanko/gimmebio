"""CLI for kmer related stuff."""

import click
import sys
from os.path import basename
import pandas as pd

from .kmer_stats import jf_stats
from .kmers import make_kmers
from .min_sparse_kmers import MinSparseKmerSet

from .clustering.cli import cli_kmer_cluster


@click.group()
def kmers():
    """Utilities for kmers."""
    pass


kmers.add_command(cli_kmer_cluster)


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


@kmers.command('stats')
@click.option('-d', '--delim', default=None, help='Delimiter for sample name in filename')
@click.argument('out_file', type=click.File('w'))
@click.argument('jellyfish_filenames', nargs=-1)
def cli_jellyfish_stats(delim, out_file, jellyfish_filenames):
    """Make a table of summary stats from jellyfish kmer counting files."""
    tbl = {}
    for jf_filename in jellyfish_filenames:
        sample_name = basename(jf_filename)
        if delim:
            sample_name = sample_name.split(delim)[0]
        tbl[sample_name] = jf_stats(jf_filename)
    tbl = pd.DataFrame.from_dict(tbl, orient='index')
    tbl.to_csv(out_file)


if __name__ == '__main__':
    kmers()
