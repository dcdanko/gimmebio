import click

from sys import stderr
from .main import *


@click.command()
@click.argument('human_genome')
@click.argument('gene_db')
@click.argument('barcoded_reads')
@click.argument('sample_name')
def main(human_genome, gene_db, barcoded_reads, sample_name):
    """Find operons."""
    print('Aligning to human genome...', file=stderr)
    unal_reads = filter_human_reads(sample_name, barcoded_reads, human_genome)
    print('Aligning to genes...', file=stderr)
    raw_aln = align_to_genes(sample_name, unal_reads, gene_db)
    print('Processing Operons...', file=stderr)
    filt_aln = filter_bad_align(sample_name, raw_aln)
    single_aln = read_to_gene_map(sample_name, filt_aln)
    rid_to_bx = get_rid_to_bx(sample_name, barcoded_reads)
    bx_to_gene = get_bx_to_gene(sample_name, rid_to_bx, single_aln)
    gene_dist = get_gene_distance(sample_name, bx_to_gene)
    find_components(sample_name, gene_dist)
