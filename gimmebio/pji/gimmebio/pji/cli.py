
import click
import pandas as pd

from .pji import identify_pji_taxa


@click.group('pji')
def pji():
    pass


@pji.command('find')
@click.option('-c', '--contam-thresh', default=0.5)
@click.option('-r', '--rank', default='species')
@click.argument('longform_taxa')
@click.argument('outfile', type=click.File('w'))
def cli_find_contams(contam_thresh, rank, longform_taxa, outfile):
    compression = 'gzip' if '.gz' in longform_taxa else None
    longtaxa = pd.read_csv(longform_taxa, compression=compression)
    longtaxa.columns = [
        'sample_name', 'taxa_name', 'taxa_id', 'rank', 'mpa',
        'reads', 'kmers', 'dup', 'cov', 'percent', 'tax_reads',
    ]
    longtaxa = longtaxa.query('kmers > 256')
    if rank:
        longtaxa = longtaxa.query(f'rank == "{rank}"')
    identified = identify_pji_taxa(longtaxa, contam_thresh=contam_thresh)
    identified.to_csv(outfile)


if __name__ == '__main__':
    pji()
