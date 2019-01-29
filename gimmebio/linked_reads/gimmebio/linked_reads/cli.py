"""CLI for linked read related stuff."""

import click

from .readcloud_io import iterReadCloud


@click.group()
def lr():
    """Utilities for linked reads."""
    pass


@lr.command('filter-bcs')
@click.option('-s', '--min-bc-size', default=0, help='Minimum size of a barcode')
@click.option('-e', '--end', default=0,
              help='Only take the first (1) or second (2) read from an interleaved file')
@click.argument('fastq_in', type=click.File('r'))
@click.argument('fastq_out', type=click.File('w'))
def cli_filter_bcs(min_bc_size, end, fastq_in, fastq_out):
    """Filter barcoded reads."""
    for read_cloud in iterReadCloud(fastq_in):
        if min_bc_size and (not read_cloud.barcode or len(read_cloud) < min_bc_size):
            continue
        for read_pair in read_cloud:
            if end == 1:
                fastq_out.write(str(read_pair.r1) + '\n')
            elif end == 2:
                fastq_out.write(str(read_pair.r2) + '\n')
            else:
                fastq_out.write(str(read_pair) + '\n')


if __name__ == '__main__':
    lr()
