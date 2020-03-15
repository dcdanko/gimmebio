
import click
from os import environ

from .api import (
    download_genomes,
    make_index,
    search_reads,
    condense_alignment,
    make_report,
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
@click.option('-o', '--outfile', default='-', type=click.File('w'))
@click.option('-b', '--blast-exc',
              default=environ.get('COVID_BLAST_EXC', 'blastn'),
              help='executable for blastn.',
              )
@click.option('-q', '--fq2fa-exc',
              default=environ.get('COVID_FQ2FA_EXC', 'fastq2fasta'),
              help='executable to convert fastq to fasta.',
              )
@click.option('-t', '--threads', default=1)
@click.argument('genome_dir', type=click.Path())
@click.argument('reads', type=click.Path())
def cli_search(outfile, blast_exc, fq2fa_exc, threads, genome_dir, reads):
    """Search reads against an index in the genome dir."""
    search_reads(
        blast_exc,
        fq2fa_exc,
        genome_dir,
        reads,
        outfile,
        threads=threads,
        logger=lambda x: click.echo(x, err=True),
    )


@covid.command('report')
@click.option('-o', '--outfile', default='coverage_report.png', type=click.Path())
@click.argument('m8_alignment', type=click.Path())
def cli_condense(outfile, m8_alignment):
    """Condense an alignment to a set of viral calls."""
    make_report(
        m8_alignment,
        outfile,
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
