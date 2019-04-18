"""CLI for linked read related stuff."""

import click
import pandas as pd

from .assign_contigs import (
    assign_contigs,
    compress_assigned_contigs,
)


@click.group()
def assembly():
    """Utilities for linked reads."""
    pass


@assembly.command('id-contigs')
@click.option('-s', '--sep', default='\t')
@click.option('-g', '--genbank-id-map', default=None)
@click.option('-f', '--seq-fasta', default=None, type=click.File('r'))
@click.argument('m8file', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
def cli_id_contigs(sep, genbank_id_map, seq_fasta, m8file, outfile):
    """ID contigs based on the species that have the most homology to each."""
    tbl = assign_contigs(m8file, genfile=genbank_id_map, seqfile=seq_fasta)
    tbl.to_csv(outfile, sep=sep)


@assembly.command('condense-ids')
@click.option('-s', '--sep', default='\t')
@click.option('-r', '--rank', default=None, help='Taxonomic rank for grouping')
@click.argument('assignement_file', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
def cli_condense_ids(sep, rank, assignment_file, outfile):
    """ID contigs based on the species that have the most homology to each."""
    tbl = pd.read_csv(assignment_file, sep=sep, index_col=0)
    tbl = compress_assigned_contigs(tbl, rank=rank)
    tbl.to_csv(outfile, sep=sep)
