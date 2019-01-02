
import click

from .histogram import text_histogram
from .scatter_plot import text_scatter_plot


@click.group()
def plots():
    pass


@plots.command('histo')
@click.option('--logy/--normaly', default=False)
@click.option('--max-pos', type=float, default=None)
@click.option('--bin-width', type=float, default=1)
@click.option('--graph-width', type=float, default=70)
@click.argument('input_file', type=click.File('r'))
def cli_text_histogram(logy, max_pos, bin_width, graph_width, input_file):
    """Print a text histogram to stdout."""
    values = []
    for line in input_file:
        try:
            values.append(float(line.strip()))
        except ValueError:
            click.echo(f'Warning: "{line.strip()}" could not be parsed', err=True)
    click.echo(text_histogram(
        values, logy=logy, max_pos=max_pos, bin_width=bin_width, graph_width=graph_width
    ))


@plots.command('scatter')
@click.option('-s', '--sep', default=' ')
@click.option('-w', '--graph-width', type=int, default=70)
@click.option('-h', '--graph-height', type=int, default=30)
@click.argument('input_file', type=click.File('r'))
def cli_text_scatter_plot(sep, graph_width, graph_height, input_file):
    """Print a text scatter plot to stdout."""
    values = []
    for line in input_file:
        try:
            x, y = line.split(sep)
            values.append((float(x), float(y)))
        except ValueError:
            click.echo(f'Warning: "{line.strip()}" could not be parsed', err=True)

    click.echo(text_scatter_plot(
        values, graph_width=graph_width, graph_height=graph_height
    ))


if __name__ == '__main__':
    plots()
