
import click

from os.path import basename
from .entropy_scores import entropy_and_clump_score, entropy_score_fastq


@click.group('entropy')
def entropy():
    """Find entropy scores for different file types."""
    pass


@entropy.command('bam')
@click.option('-d', '--delim', default=None)
@click.option('-g', '--genome-delim', default='::')
@click.option('-t', '--tag', default=None)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('bams', nargs=-1)
def cli_entropy_scores_from_bam(delim, genome_delim, tag, outfile, bams):
    tbl = {}
    for bam in bams:
        sname = basename(bam)
        if delim:
            sname = sname.split(delim)[0]
        tbl[sname] = entropy_and_clump_score(bam, delim=genome_delim)
    for sname, (escores, cscores) in tbl.items():
        for genome, cscore in cscores:
            escore = escores[genome]
            if tag:
                print(f'{sname},{genome},{tag},{escore},{cscore}', file=outfile)
            else:
                print(f'{sname},{genome},{escore},{cscore}', file=outfile)


@entropy.command('fastq')
@click.option('-d', '--delim', default=None)
@click.option('-g', '--genome-delim', default='::')
@click.option('-t', '--tag', default=None)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('fastqs', nargs=-1)
def cli_entropy_scores_from_fastq(delim, genome_delim, tag, outfile, fastqs):
    tbl = {}
    for fastq in fastqs:
        sname = basename(fastq)
        if delim:
            sname = sname.split(delim)[0]
        tbl[sname] = entropy_score_fastq(fastq, delim=genome_delim)
    for sname, escores in tbl.items():
        for genome, escore in escores:
            if tag:
                print(f'{sname},{genome},{tag},{escore}', file=outfile)
            else:
                print(f'{sname},{genome},{escore}', file=outfile)


if __name__ == '__main__':
    cli_entropy_scores()
