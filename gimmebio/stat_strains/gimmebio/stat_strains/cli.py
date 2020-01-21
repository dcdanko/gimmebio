
import click
import pandas as pd

from os.path import basename

from .api import (
    entropy_reduce_postion_matrices,
    entropy_reduce_position_matrix,
)
from .metrics import scaling_manhattan


@click.group('stat-strains')
def stat_strains():
    pass


@stat_strains.command('reduce')
@click.option('-r', '--radius', default=0.01)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('filename')
def reduce(radius, outfile, filename):

        def logger(n_centroids, n_cols):
            if (n_cols % 100) == 0:
                click.echo(f'{n_centroids} centroids, {n_cols} columns', err=True)

        matrix = pd.read_csv(filename, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            matrix,
            radius,
            scaling_manhattan,
            logger=logger
        )
        click.echo(full_reduced.shape, err=True)
        full_reduced.to_csv(outfile)


@stat_strains.command('concat-tables')
@click.option('-r', '--radius', default=0.01)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('filenames', nargs=-1)
def concat_tables(radius, outfile, filenames):

        def _parse_matrix(filehandle):
            matrix = pd.read_csv(filehandle, index_col=0, header=0)
            pref = basename(filehandle) + '__'
            matrix.columns = [pref + el for el in matrix.columns]
            return matrix

        full_reduced = entropy_reduce_postion_matrices(
            filenames,
            radius,
            scaling_manhattan,
            matrix_parser=_parse_matrix,
            logger=lambda x: click.echo(x, err=True)
        )
        click.echo(full_reduced.shape, err=True)
        full_reduced.to_csv(outfile)


if __name__ == '__main__':
    stat_strains()
