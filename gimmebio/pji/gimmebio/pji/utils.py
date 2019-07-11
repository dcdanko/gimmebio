
import numpy as np


def get_mad(vals, constant=1.4826):
    """Return a tuple of (median, mad) for the series."""
    med = np.median(vals)
    diffs = abs(vals - med)
    med_dev = constant * np.median(diffs)
    return med, med_dev
