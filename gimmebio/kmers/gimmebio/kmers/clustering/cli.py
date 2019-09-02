
import click
from time import clock
import pandas as pd

from gimmebio.ram_seq import rs_matrix, seq_power_series
from gimmebio.sample_seqs import EcoliGenome
from gimmebio.kmers import make_kmers

from .eval_clustering import radial_cover_cluster, eval_kd_cluster


@click.group('cluster')
def cli_kmer_cluster():
    pass


@cli_kmer_cluster.command('eval-radial')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
def eval_radial_kmer_cluster(outfile):
    pass


@cli_kmer_cluster.command('eval-kdrft')
@click.option('-k', '--kmer-len', default=32)
@click.option('-n', '--num-kmers', default=1000, help='Number of kmers to cluster.')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
def eval_kdrft_cluster(kmer_len, num_kmers, outfile):
    ecoli_kmers = make_kmers(
        EcoliGenome().longest_contig()[:kmer_len + num_kmers + 1000 - 1],
        kmer_len, canon=True
    )
    print(f'Made {len(ecoli_kmers)} E. coli k-mers for testing')

    tbl = [el for el in eval_kd_cluster(ecoli_kmers) if print(el) or True]
    tbl = pd.DataFrame(tbl)
    tbl.to_csv(outfile)


@cli_kmer_cluster.command('time-ramify')
def cli_time_ramify():
    ecoli_kmers = make_kmers(EcoliGenome().longest_contig()[:10131], 32, canon=True)
    print(f'Made {len(ecoli_kmers)} k-mers for testing')

    start = clock()
    rfts = []
    rf_coeffs = rs_matrix(32)
    for kmer in ecoli_kmers:
        rfts.append(seq_power_series(kmer, RS=rf_coeffs)[:min(16, len(kmer))])
    elapsed = clock() - start
    print(elapsed)

