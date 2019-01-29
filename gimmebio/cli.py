# -*- coding: utf-8 -*-

"""Console script for metasub_utils."""

import click
from sys import stderr

VERBOSE = True


@click.group()
def main(args=None):
    """Console script for gimmebio."""
    pass


sub_clis = [
    ('gimmebio.kmers.cli', 'kmers'),
    ('gimmebio.seqs.cli', 'seqs'),
    ('gimmebio.text_plots.cli', 'plots'),
    ('gimmebio.linked_reads.cli', 'lr'),
]


def add_submodule_cli(module_name, cli_main_name):
    try:
        cli_module = __import__(module_name, fromlist=[''])
        main.add_command(getattr(cli_module, cli_main_name))
    except ImportError:
        if VERBOSE:
            print(f'Unable to import {module_name}', file=stderr)


for module_name, cli_main_name in sub_clis:
    add_submodule_cli(module_name, cli_main_name)


if __name__ == "__main__":
    main()
