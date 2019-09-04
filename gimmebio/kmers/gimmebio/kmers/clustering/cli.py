
import click
from time import clock
import pandas as pd

from json import dumps

from gimmebio.ram_seq import rs_matrix, seq_power_series
from gimmebio.sample_seqs import EcoliGenome
from gimmebio.kmers import make_kmers

from .eval_clustering import radial_cover_cluster, eval_kd_cluster
from .kd_rft_cover import KDRFTCover

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


@cli_kmer_cluster.command('build-kdrft')
@click.option('-r', '--radius', default=0.1)
@click.option('-k', '--kmer-len', default=31)
@click.option('-o', '--outfile', default='-', type=click.File('w'))
@click.argument('kmer_table', type=click.File('r'))
def build_kdrft_cluster(radius, kmer_len, outfile, kmer_table):
    kdrft_cover = KDRFTCover(radius)
    for line in kmer_table:
        kmer = line.strip().split(',')[0]
        kdrft_cover.add(kmer)
    click.echo('Added kmers to cover.', err=True)
    kdrft_cover.greedy_clusters(logger=lambda el: click.echo(el, err=True))
    click.echo(pd.Series(kdrft_cover.stats()), err=True)
    cover_as_dict = kdrft_cover.to_dict()
    print(dumps(cover_as_dict), file=outfile)


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

