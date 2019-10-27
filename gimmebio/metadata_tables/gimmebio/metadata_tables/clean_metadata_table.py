import numpy as np
import pandas as pd


def quantize_values(vals, nbins=None):
    """Return a list of values mapped to discrete ranges.

    Get as close to 10 items per bin as possible if not specified.
    """
    if not nbins:
        nbins = len(vals) // 10

    bin_ends = np.linspace(min(vals), max(vals) + 1, num=nbins)
    binned = []
    for val in vals:
        for i, bin_end in enumerate(bin_ends):
            if val < bin_end:
                bin_name = f'{bin_ends[i - 1]} - {bin_end}'
                binned.append(bin_name)
    return binned


def split_nested_lists(vals, sep=';'):
    """Return a boolean data frame from a list of values with nested quantities."""
    split_tbl = []
    for val in vals:
        sub_vals = val.split(sep)
        split_tbl.append({sub_val.strip(): True for sub_val in sub_vals})
    return pd.DataFrame(split_tbl)


def booleanize_list(vals, null_vals=['no', 'none', 'na', 'n/a', '']):
    """Return a list of true/false from values."""
    out = []
    for val in vals:
        val = val.strip().lower()
        out.append(val and val not in null_vals)
    return out


def remap_vals(vals, val_map):
    """Return a list with vals in val_map remapped."""
    return [val_map.get(val.lower(), val) for val in vals]

