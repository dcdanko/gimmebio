"""CLI for seq related stuff."""

import click

from sys import stderr
from os.path import basename


@click.group()
def seqs():
    """Utilities for kmers."""
    pass


@seqs.command('iter-paired-end')
@click.option('-s/-n', '--sample-names/--no-sample-names', default=False)
@click.argument('filenames', type=click.File('r'))
def iter_paired_end_filenames(sample_names, filenames):
    """Print paired end files to stdout, one pair per line.

    Print unpaired files to stderr.
    """
    def get_sample_name_and_end(filename):
        """Return a tuple of sample name and read end."""
        base = basename(filename)
        for pattern, end in [('.R1.', 1), ('_1.', 1), ('.R2.', 2), ('_2.', 2)]:
            if pattern in base:
                return base.split(pattern)[0], end
        assert False  # pattern unknown

    tbl = {}
    for filename in filenames:
        filename = filename.strip()
        try:
            sample_name, end = get_sample_name_and_end(filename)
            try:
                tbl[sample_name][end - 1] = filename
            except KeyError:
                tbl[sample_name] = [None, None]
                tbl[sample_name][end - 1] = filename
        except AssertionError:
            print(f'[UNKNOWN PATTERN]\t{filename}', file=stderr)

    for sample_name, (r1, r2) in tbl.items():
        if r1 is None or r2 is None:
            print(f'[UNPAIRED SAMPLE]\t{sample_name}\t{r2 if r1 is None else r1}', file=stderr)
            continue
        out_str = f'{r1}\t{r2}'
        if sample_names:
            out_str = f'{sample_name}\t{out_str}'
        print(out_str)


if __name__ == '__main__':
    seqs()
