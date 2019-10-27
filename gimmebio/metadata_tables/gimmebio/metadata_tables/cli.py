"""Not actually a CLI yet, someday."""

import numpy as np
import pandas as pd
import click


NULL_VALS = ['no', 'none', 'na', 'n/a', '', 'nan']


def quantize_values(vals, nbins=None):
    """Return a list of values mapped to discrete ranges.

    Get as close to 10 items per bin as possible if not specified.
    """
    if not nbins:
        nbins = len(vals) // 10

    not_null = [val for val in vals if str(val).lower() not in NULL_VALS]
    bin_ends = np.linspace(min(not_null), max(not_null) + 1, num=(nbins + 1))
    binned = []
    for val in vals:
        if not val or str(val).lower() in NULL_VALS:
            binned.append(val)
            continue
        for i, bin_end in enumerate(bin_ends):
            if val < bin_end:
                bin_name = f'{int(bin_ends[i - 1])} - {int(bin_end)}'
                binned.append(bin_name)
                break
    return binned


def split_nested_lists(vals, sep=';'):
    """Return a boolean data frame from a list of values with nested quantities."""
    split_tbl = []
    for val in vals:
        sub_vals = str(val).split(sep)
        split_tbl.append({sub_val.strip(): True for sub_val in sub_vals})
    return pd.DataFrame(split_tbl)


def booleanize_list(vals, null_vals=NULL_VALS):
    """Return a list of true/false from values."""
    out = []
    for val in vals:
        val = str(val).strip().lower()
        out.append(val and val not in null_vals)
    return out


def remap_vals(vals, val_map):
    """Return a list with vals in val_map remapped."""
    return [val_map.get(str(val).lower().strip(), val) for val in vals]



@click.command()
@click.argument('table')
def main(table):
    table = pd.read_csv(table, index_col=0)
    bool_cols = [
        'Smoker', 'Antibiotics', 'Purell Phone', 'Purell Hands',
        'Skin Conditions', 'Illness', 'Outdoors', 'Mass Transit Use'
    ]
    for col_name in bool_cols:
        foo = booleanize_list(table[col_name])
        table[col_name] = foo

    quant_cols = [('Age', 5)]
    for col_name, nbins in quant_cols:
        foo = quantize_values(table[col_name], nbins=nbins)
        click.echo(foo, err=True)
        click.echo(len(foo), err=True)
        click.echo(len(table[col_name]), err=True)
        table[col_name] = foo

    remap_cols = [('Children', {'no': 0, 'zero': 0, 'none': 0})]
    for col_name, val_map in remap_cols:
        table[col_name] = remap_vals(table[col_name], val_map)

    table['Children'] = [el.split(',')[1].strip() if el is str else el for el in table['Children']]

    split_cols = [('Food', ','), ('Pets', ','), ('Social Media', ',')]
    for col_name, sep in split_cols:
        vals = table[col_name]
        del table[col_name]
        pd.concat([table, split_nested_lists(vals, sep=sep)])

    print(table.to_csv())


if __name__ == '__main__':
    main()
