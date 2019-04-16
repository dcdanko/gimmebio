"""CLI for linked read related stuff."""

import click

from .assign_contigs import assign_contigs


@click.group()
def assembly():
    """Utilities for linked reads."""
    pass


@assembly.command('id-contigs')
@click.option('-s', '--sep', default='\t')
@click.option('-g', '--genbank_id_map', default=None)
@click.argument('m8file', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
def cli_id_contigs(sep, genbank_id_map, m8file, outfile):
    """ID contigs based on the species that have the most homology to each."""
    tbl = assign_contigs(m8file, genfile=genbank_id_map)
    tbl.to_csv(outfile, sep=sep)
