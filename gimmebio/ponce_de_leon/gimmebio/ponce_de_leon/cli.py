
# -*- coding: utf-8 -*-

"""Console script for ponce_de_leon."""

import click
from sys import stdout, stdin
from .api import (
    get_bcs_in_region,
    get_reads_with_bcs_fastq,
    get_reads_with_bcs_sam,
    count_kmer_classes,
)
from pandas import DataFrame


@click.group()
def main():
    """Console script for ponce_de_leon."""
    pass


@main.group()
def filter():
    """Group for filter commands."""
    pass


@filter.command('bc-by-region')
@click.option('-f', '--fastq-file', default=None, type=click.File('r'))
@click.argument('bed_file', type=click.File('r'))
@click.argument('sam_file', default=stdin, type=click.File('rb'))
def bc_by_region(fastq_file, bed_file, sam_file):
    """Produce a barcode list where each bc has a read within a region."""
    for bc in get_bcs_in_region(sam_file, bed_file, fastq_file=fastq_file):
        print(bc)


@filter.command('read-by-bc')
@click.argument('bc_list', type=click.File('r'))
@click.argument('fastq', default=stdin, type=click.File('r'))
def read_by_bc(bc_list, fastq):
    """Remove reads that do not have a specified barcode."""
    for seq_chunk in get_reads_with_bcs_fastq(bc_list, fastq):
        for line in seq_chunk:
            stdout.write(line)


@filter.command('sam-by-bc')
@click.argument('bc_list', type=click.File('r'))
@click.argument('sam', default=stdin, type=click.File('r'))
def sam_by_bc(bc_list, sam):
    """Remove reads that do not have a specified barcode."""
    get_reads_with_bcs_sam(bc_list, sam)


@main.command('kmerize')
@click.option('-s/-f', '--sam-file/--fastq-file', default=False)
@click.option('-k', default=6, type=int, help='K to generate kmers')
@click.argument('fastq')
def kmerize(sam_file, k, fastq):
    """Count high abundance kmers."""
    kmer_table = count_kmer_classes(fastq, k=k, sam=sam_file)
    kmer_table = DataFrame.from_dict(kmer_table, orient='index')
    stdout.write(kmer_table.to_csv())


@main.command('rotate-kmers')
@click.argument('jf_file')
def kmerize(jf_file):
    """Use an existing jellyfish file to break kmers into rotationally equivalent classes."""
    kmer_table = count_kmer_classes(jf_file, rotations=True)
    kmer_table = DataFrame.from_dict(kmer_table, orient='index')
    stdout.write(kmer_table.to_csv())


if __name__ == "__main__":
    main()
