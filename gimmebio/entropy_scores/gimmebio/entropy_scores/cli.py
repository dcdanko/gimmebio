
import click

from os.path import basename
from .entropy_scores import entropy_score


@click.command('entropy')
@click.option('-d', '--delim', default=None)
@click.argument('outfile', type=click.File('w'))
@click.argument('bams', nargs=-1)
def cli_entropy_scores(delim, outfile, bams):
    tbl = {}
    for bam in bams:
        sname = basename(bam)
        if delim:
            sname = sname.split(delim)[0]
        tbl[sname] = entropy_score(bam)
    for key, val in tbl.items():
        print(f'{key},{val}', file=outfile)


if __name__ == '__main__':
    cli_entropy_scores()
