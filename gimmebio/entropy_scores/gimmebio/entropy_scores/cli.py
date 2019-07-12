
import click

from os.path import basename
from .entropy_scores import entropy_and_clump_score


@click.command('entropy')
@click.option('-d', '--delim', default=None)
@click.option('-t', '--tag', default=None)
@click.argument('outfile', type=click.File('w'))
@click.argument('bams', nargs=-1)
def cli_entropy_scores(delim, tag, outfile, bams):
    tbl = {}
    for bam in bams:
        sname = basename(bam)
        if delim:
            sname = sname.split(delim)[0]
        tbl[sname] = entropy_and_clump_score(bam)
    for sname, (escore, cscore) in tbl.items():
        if tag:
            print(f'{sname},{tag},{escore},{cscore}', file=outfile)
        else:
            print(f'{sname},{escore},{cscore}', file=outfile)


if __name__ == '__main__':
    cli_entropy_scores()
