
import click
import pandas as pd

from os.path import basename

from .api import (
    entropy_reduce_postion_matrices,
    entropy_reduce_position_matrix,
    fast_entropy_reduce_postion_matrices,
    filter_concat_matrices,
)


@click.group('stat-strains')
def stat_strains():
    pass


@stat_strains('concat')
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('files', nargs=-1)
def concat_matrices(outfile, files):
    tbl = filter_concat_matrices(files)
    outfile.to_csv(outfile)


@stat_strains.command('reduce')
@click.option('-m', '--metric', default='cosine')
@click.option('-r', '--radius', default=0.01)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('filename')
def reduce(metric, radius, outfile, filename):

        def logger(n_centroids, n_cols):
            if (n_cols % 100) == 0:
                click.echo(f'{n_centroids} centroids, {n_cols} columns', err=True)

        matrix = pd.read_csv(filename, index_col=0, header=0)
        full_reduced = entropy_reduce_position_matrix(
            matrix,
            radius,
            metric,
            logger=logger
        )
        click.echo(full_reduced.shape, err=True)
        full_reduced.to_csv(outfile)


@stat_strains.command('concat-tables')
@click.option('-m', '--metric', default='cosine')
@click.option('-r', '--radius', default=0.01)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('filenames', nargs=-1)
def concat_tables(metric, radius, outfile, filenames):

        def _parse_matrix(filehandle):
            matrix = pd.read_csv(filehandle, index_col=0, header=0)
            matrix = matrix.T[matrix.sum() > 0].T
            pref = basename(filehandle) + '__'
            matrix.columns = [pref + el for el in matrix.columns]
            return matrix

        full_reduced = entropy_reduce_postion_matrices(
            filenames,
            radius,
            metric,
            matrix_parser=_parse_matrix,
            logger=lambda x: click.echo(x, err=True)
        )
        click.echo(full_reduced.shape, err=True)
        full_reduced.to_csv(outfile)


@stat_strains.command('fast-concat-tables')
@click.option('-m', '--metric', default='cosine')
@click.option('-l/-n', '--file-list/--names', default=False,
    help='Interpret filenames as lists of filenames instead of the names themselves')
@click.option('-r', '--radius', default=0.01)
@click.option('-o', '--outfile', type=click.File('w'), default='-')
@click.argument('filenames', nargs=-1)
def fast_concat_tables(metric, file_list, radius, outfile, filenames):
        if file_list:
            names = []
            for filename in filenames:
                with open(filename) as f:
                    names += [line.strip() for line in f]
            filenames = names

        def _parse_matrix(filehandle):
            matrix = pd.read_csv(filehandle, index_col=0, header=0)
            pref = basename(filehandle) + '__'
            matrix.columns = [pref + el for el in matrix.columns]
            return matrix

        full_reduced = fast_entropy_reduce_postion_matrices(
            filenames,
            radius,
            metric,
            matrix_parser=_parse_matrix,
            logger=lambda x: click.echo(x, err=True)
        )
        click.echo(full_reduced.shape, err=True)
        full_reduced.to_csv(outfile)


if __name__ == '__main__':
    stat_strains()
