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
    ('gimmebio.assembly.cli', 'assembly'),
    ('gimmebio.pji.cli', 'pji'),
    ('gimmebio.entropy_scores.cli', 'entropy'),
    # ('gimmebio.stat_strains.cli', 'stat_strains'),
    ('gimmebio.covid.cli', 'covid'),
]


def add_submodule_cli(module_name, cli_main_name):
    try:
        cli_module = __import__(module_name, fromlist=[''])
        main.add_command(getattr(cli_module, cli_main_name))
    except ImportError:
        if VERBOSE:
            print(f'Unable to import {module_name}', file=stderr)
    except:
        print(f'Other error importing {module_name}', file=stderr)


for module_name, cli_main_name in sub_clis:
    try:
        add_submodule_cli(module_name, cli_main_name)
    except:
        print(f'Error adding {module_name}', file=stderr)


if __name__ == "__main__":
    main()
