import click
from sys import stdout, stderr
from json import loads, dumps
import pandas as pd
from .normalizer import normalizeTaxa, OptimizationFailedError


def jloads(fname):
    return loads(open(fname).read())


def clipTable(tbl, ncols):
    vals = tbl.sum(axis=0)
    cutoff = sorted(vals, reverse=True)[ncols-1]
    keep = vals >= cutoff
    return tbl.ix[:, keep]


@click.command()
@click.option('-n', '--num-taxa', default=100, type=int,
              help='restrict normalization to the N most abundant taxa')
@click.option('--restrict-taxa-size/--no-restrict-taxa-size', default=True,
              help='Restrict taxa AGS from 1M to 10MB')
@click.argument('ave_genome_size')
@click.argument('taxa_table_json')
def main(num_taxa, restrict_taxa_size, ave_genome_size, taxa_table_json):
    ags = jloads(ave_genome_size)
    ags = pd.Series(ags).as_matrix()
    obj = jloads(taxa_table_json)
    normed = {}
    for level, tbl in obj.items():
        billionth = 1 / (1000 * 1000 * 1000)
        tbl = pd.DataFrame(tbl).fillna(0)
        tbl = tbl / tbl.sum(axis=0)
        tbl = tbl.transpose()
        tbl = clipTable(tbl, num_taxa)
        stderr.write('Normalizing {} {}... '.format(level, tbl.shape))        
        try:
            normTaxa, taxaVec = normalizeTaxa(tbl, ags, taxaBounds=restrict_taxa_size)
            normed[level] = {'taxa_ags': taxaVec.to_dict(),
                             'normalized': normTaxa.to_dict()}
            stderr.write('success.\n')
        except OptimizationFailedError as ofe:
            normed[level] = 'normalization_failed'
            stderr.write('failure. {}\n'.format(ofe))
    stdout.write(dumps(normed))


if __name__ == '__main__':
    main()
