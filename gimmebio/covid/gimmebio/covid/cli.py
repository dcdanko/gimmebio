
import click
from os import environ

from .api import (
    download_genomes,
    make_index,
    search_reads,
    condense_alignment,
)


@click.group()
def covid():
    pass


@covid.command('download')
@click.argument('target_dir', type=click.Path())
def cli_download_genomes(target_dir):
    """Download reference genomes for COVID19 pipeline to target dir."""
    download_genomes(target_dir, logger=lambda x: click.echo(x, err=True))


@covid.command('index')
@click.option('-b', '--makeblastdb-exc',
              default=environ.get('COVID_MAKEBLASTDB_EXC', 'makeblastdb'),
              help='executable to makeblastdb.',
              )
@click.argument('genome_dir', type=click.Path())
def cli_makeblastdb(makeblastdb_exc, genome_dir):
    """Make a blastdb from all fastas in genome_dir."""
    make_index(makeblastdb_exc, genome_dir, logger=lambda x: click.echo(x, err=True))


@covid.command('search')
@click.option('-o', '--outfilename', default='-')
@click.option('-b', '--blast-exc',
              default=environ.get('COVID_BLAST_EXC', 'blastn'),
              help='executable for blastn.',
              )
@click.argument('genome_dir', type=click.Path())
@click.argument('reads', type=click.Path())
def cli_search(outfilename, blast_exc, genome_dir, reads):
    """Search reads against an index in the genome dir."""
    search_reads(
        blast_exc,
        genome_dir,
        reads,
        outfilename,
        logger=lambda x: click.echo(x, err=True),
    )


@covid.command('condense')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
@click.argument('m8_alignment', type=click.Path())
def cli_condense(outfile, m8_alignment):
    """Condense an alignment to a set of viral calls."""
    condense_alignment(
        outfile,
        m8_alignment,
        logger=lambda x: click.echo(x, err=True),
    )
