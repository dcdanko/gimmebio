
import click
from gimmebio.sample_seqs import EcoliGenome
from gimmebio.kmers import make_kmers

from .eval_clustering import radial_cover_cluster, kd_cluster


@click.group('cluster')
def cli_kmer_cluster():
    pass


@cli_kmer_cluster.command('eval-radial')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
def eval_radial_kmer_cluster(outfile):

    ecoli_kmers = make_kmers(EcoliGenome().longest_contig(), 21, canon=True)
    print(f'Made {len(ecoli_kmers)} k-mers for testing')

    class KmerGenerator:

        def __init__(self, kmers):
            self.i = 0
            self.kmers = kmers

        def generate(self):
            kmer = self.kmers[self.i]
            self.i += 1
            return kmer

    kmer_generator = KmerGenerator(ecoli_kmers)

    tbl = radial_cover_cluster(kmer_generator.generate)
    tbl.to_csv(outfile)


@cli_kmer_cluster.command('eval-kdrft')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
def eval_kdrft_cluster(outfile):

    ecoli_kmers = make_kmers(EcoliGenome().longest_contig()[:400000], 32, canon=True)
    print(f'Made {len(ecoli_kmers)} k-mers for testing')

    class KmerGenerator:

        def __init__(self, kmers):
            self.i = 0
            self.kmers = kmers

        def generate(self):
            kmer = self.kmers[self.i]
            self.i += 1
            return kmer

    kmer_generator = KmerGenerator(ecoli_kmers)

    for tbl in kd_cluster(kmer_generator.generate):
        tbl.to_csv(outfile)
