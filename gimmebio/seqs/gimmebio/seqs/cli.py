"""CLI for seq related stuff."""

import click

from sys import stderr, stdout
from os.path import basename

from .sample_management import get_sample_name_and_end
from .concat_lanes import (
    group_filenames_by_name_read_lane,
    concatenate_grouped_filenames,
)

@click.group()
def seqs():
    """Utilities for kmers."""
    pass


@seqs.command('highlight')
@click.argument('sequence_file', type=click.File('r'))
def highlight_DNA(sequence_file):
    """Highlight bases in a DNA sequence."""
    COLS, ENDC = {'A': '\033[31m', 'T': '\033[33m', 'C': '\033[32m', 'G': '\033[34m'}, '\033[0m'
    for line in sequence_file:
        for base in line:
            try:
                col = COLS[base.upper()]
                stdout.write(col + base + ENDC)
            except KeyError:
                stdout.write(base)


@seqs.command('get-sample-names')
@click.option('-r/-n', '--read-number/--no-read-number', default=False)
@click.option('-f/-s', '--keep-filename/--no-keep-filename', default=False)
@click.argument('fastq_filenames_file', type=click.File('r'))
def get_sample_names(read_number, keep_filename, fastq_filenames_file):
    """Print the sample name of samples in file."""
    for fastq_filename in fastq_filenames_file:
        sample_name, end = get_sample_name_and_end(fastq_filename)
        out_str = sample_name
        if read_number:
            out_str += f'\t{end}'
        if keep_filename:
            out_str += f'\t{fastq_filename}'
        print(out_str)


@seqs.command('iter-paired-end')
@click.option('-s/-n', '--sample-names/--no-sample-names', default=False)
@click.argument('filenames', type=click.File('r'))
def iter_paired_end_filenames(sample_names, filenames):
    """Print paired end files to stdout, one pair per line.

    Print unpaired files to stderr.
    """
    tbl = {}
    for filename in filenames:
        filename = filename.strip()
        try:
            sample_name, end = get_sample_name_and_end(filename)
            if not end:
                print(f'[SINGLE ENDED]\t{filename}', file=stderr)
                continue
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


@seqs.command('concat-lanes')
@click.option('-d/-w', '--dryrun/--wetrun', default=True)
@click.argument('dest_dir')
@click.argument('filenames', nargs=-1)
def cli_concat_lanes(dryrun, dest_dir, filenames):
    """Concatenate filenames (or at least write commands to stdout)."""
    grouped = group_filenames_by_name_read_lane(filenames)
    concatenate_grouped_filenames(grouped, dryrun=dryrun, dest_dir=dest_dir)


if __name__ == '__main__':
    seqs()
