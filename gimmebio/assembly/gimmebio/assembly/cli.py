"""CLI for linked read related stuff."""

import click
import pandas as pd
from Bio import SeqIO

from .assign_contigs import (
    assign_contigs,
    compress_assigned_contigs,
)
from .filter_process import (
    filter_homologous,
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
@click.argument('assignment_file', type=click.File('r'))
@click.argument('outfile', type=click.File('w'))
def cli_condense_ids(sep, rank, assignment_file, outfile):
    """ID contigs based on the species that have the most homology to each."""
    tbl = pd.read_csv(assignment_file, sep=sep, index_col=0)
    tbl = compress_assigned_contigs(tbl, rank=rank)
    tbl.to_csv(outfile, sep=sep)


@assembly.command('cat-fastas')
@click.option('-d', '--delim', default='::')
@click.option('-l', '--min-len')
@click.argument('outfile', type=click.File('w'))
@click.argument('fasta_files', type=click.File('r'), nargs=-1)
def cli_cat_fastas(delim, min_len, outfile, fasta_files):
    """Concatenate fastas, adding filenames to ids.

    For convenience also filter by length.
    """
    def seq_gen():
        for fasta_file in fasta_files:
            for rec in SeqIO.parse(fasta_files, 'fasta'):
                if len(rec.seq) < min_len:
                    continue
                rec.id = f'{fasta_file.name}{delim}{rec.id}'
                yield rec

    SeqIO.write(seq_gen, outfile, 'fasta')


@assembly.command('filter-homologous')
@click.option('-p', '--min-perc-id', default=0.95)
@click.option('-l', '--min-len-frac', default=0.8)
@click.argument('outfile', type=click.File('w'))
@click.argument('m8file', type=click.File('r'))
@click.argument('fasta_file', type=click.File('r'))
def cli_filter_homologous(min_perc_id, min_len_frac, outfile, m8file, fasta_file):
    """Filter contigs that are homologous to one another keeping the largest.

    Find connected components in the m8 file (presumed to be an
    autologous alignment). Edges exist between contigs where
    an alignment is:
    1) Greater than <min_perc_id> similar
    2) Longer than <min_len_frac> * min(len(c1), len(c2))
    For each component take the longest contig and write it to a fasta.
    """
    SeqIO.write(
        filter_homologous(m8file, fasta_file, min_perc_id=min_perc_id, min_len_frac=min_len_frac),
        outfile,
        'fasta'
    )


@assembly.command('rpkm-from-bam')
@click.option('-s', '--sep', default='\t')
@click.option('-d', '--delim', default=None)
@click.argument('outfile', type=click.File('w'))
@click.argument('bams', type=click.File('rb'))
def cli_rpkm_from_bam(sep, delim, outfile, bams):
    """Create a table of RPKMS from bam files.

    Assumes bam files have alignment records for each read.
    Only takes primary alignment.
    """
    pass
