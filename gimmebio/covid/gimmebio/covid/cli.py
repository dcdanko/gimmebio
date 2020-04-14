
import click
import pysam
import pandas as pd
from os import environ
from plotnine import *
from .svs import (
    tabulate_split_read_signatures,
)

from .api import (
    download_genomes,
    download_kraken2,
    make_index,
    search_reads,
    condense_alignment,
    make_report,
    kraken2_search_reads,
)


@click.group()
def covid():
    pass


@covid.group('sv')
def cli_sv():
    pass


@cli_sv.command('split-reads')
@click.option('-g', '--min-gap', default=100)
@click.option('-p/-a', '--primary/--all', default=False)
@click.option('-o', '--outfile', default='-', type=click.File('w'))
@click.argument('bams', nargs=-1)
def cli_split_reads(min_gap, primary, outfile, bams):
    tbls = []
    for bam in bams:
        click.echo(bam, err=True)
        samfile = pysam.AlignmentFile(bam, "rb")
        tbl = tabulate_split_read_signatures(samfile, min_gap=min_gap, primary_only=primary)
        tbl['sample_name'] = bam.split('/')[-1].split('.')[0]
        tbls.append(tbl)
    tbl = pd.concat(tbls)
    click.echo(tbl.shape, err=True)
    tbl.to_csv(outfile)


@cli_sv.command('plot-split')
@click.option('-o', '--outfile', default='-', type=click.File('wb'))
@click.argument('tbl')
def cli_split_reads(outfile, tbl):
    tbl = pd.read_csv(tbl, index_col=0)
    tbl = tbl.groupby('sample_name').apply(lambda t: t.sample(min(1000, t.shape[0])))
    plot = (
        ggplot(tbl, aes(x='min_pos', y='max_pos', color='sample_name')) +
            geom_point(size=2, alpha=0.1) +
            geom_density_2d(color='black') +
            ylab('Rightmost Position') +
            xlab('Leftmost Position') +
            ggtitle('Split Signature') + 
            scale_color_brewer(type='qualitative', palette=6) +
            labs(color='Sample') +
            theme(
                text=element_text(size=20),
                legend_position='right',
                figure_size=(12, 8),
                panel_border=element_rect(colour="black", fill='none', size=1),
            )
    )
    plot.save(outfile)


@covid.command('download')
@click.argument('target_dir', type=click.Path())
def cli_download_genomes(target_dir):
    """Download reference genomes for COVID19 pipeline to target dir."""
    download_genomes(target_dir, logger=lambda x: click.echo(x, err=True))
    download_kraken2(target_dir, logger=lambda x: click.echo(x, err=True))


@covid.command('index')
@click.option('-b', '--makeblastdb-exc',
              default=environ.get('COVID_MAKEBLASTDB_EXC', 'makeblastdb'),
              help='executable to makeblastdb.',
              )
@click.argument('genome_dir', type=click.Path())
def cli_makeblastdb(makeblastdb_exc, genome_dir):
    """Make a blastdb from all fastas in genome_dir."""
    make_index(makeblastdb_exc, genome_dir, logger=lambda x: click.echo(x, err=True))


@covid.command('fast-search')
@click.option('-o', '--outfile', default='-', type=click.File('w'))
@click.option('-b', '--kraken-exc',
              default=environ.get('COVID_KRAKEN2_EXC', 'kraken2'),
              help='executable for kraken2.',
              )
@click.option('-t', '--threads', default=1)
@click.argument('genome_dir', type=click.Path())
@click.argument('reads', type=click.Path())
def cli_search(outfile, kraken_exc, fq2fa_exc, threads, genome_dir, reads):
    """Search reads against an index in the genome dir."""
    kraken2_search_reads(
        kraken_exc,
        genome_dir,
        reads,
        outfile,
        threads=threads,
        logger=lambda x: click.echo(x, err=True),
    )


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
