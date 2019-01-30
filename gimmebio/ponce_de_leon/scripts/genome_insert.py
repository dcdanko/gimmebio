
import click
import pandas as pd
from Bio.SeqIO import parse, write
from random import randint, choice

TENMIL = 10 * 1000 * 1000
REGION_SIZES = [1000, 2 * 1000, 4 * 1000, 8 * 1000, 16 * 1000, 32 * 1000]


def insert_repetitive_regions(seq_rec, window_size=TENMIL, region_sizes=REGION_SIZES):
    """Insert repetitive regions into seq_rec in place. Return their coordinates."""
    nwindows, regions = len(seq_rec.seq) // window_size, {}
    if not nwindows:
        return
    for i in range(nwindows):
        window_start, window_end = window_size * i, window_size * (i + 1)
        region_start = randint(window_start + window_size / 4, window_end - window_size / 4)
        before_region, after_region = seq_rec.seq[:region_start], seq_rec.seq[region_start:]
        region_size = choice(region_sizes)
        seq_rec.seq = before_region + 'A' * region_size + after_region
        regions[(seq_rec.id, i)] = {
            'region_start': region_start,
            'region_size': region_size,
            'motif': 'A',
        }
    return pd.DataFrame.from_dict(regions, orient='index')


@click.command()
@click.argument('fasta_in', type=click.File('r'))
@click.argument('fasta_out', type=click.File('w'))
@click.argument('report', type=click.File('w'))
def main(fasta_in, fasta_out, report):
    """Insert repetitive sequences into a fasta file."""
    tbls = []
    recs = [rec for rec in parse(fasta_in, 'fasta') if len(rec.seq) >= TENMIL]
    with click.progressbar(recs) as seq_recs:
        for rec in seq_recs:
            tbls.append(insert_repetitive_regions(rec))
    tbl = pd.concat(tbls)
    tbl.to_csv(report)
    write(recs, fasta_out, 'fasta')


if __name__ == '__main__':
    main()
