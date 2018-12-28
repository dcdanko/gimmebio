from math import gcd
import numpy as np
from .utils import memoize


@memoize
def phi(n):
    """Return the Euler's totient of n."""
    amount = 0
    for k in range(1, n + 1):
        if gcd(n, k) == 1:
            amount += 1
    return amount


def ram_sum(n, q):
    """Return the ramanujan sum of (n, q)."""
    c_q = [
        np.exp(2 * 1j * np.pi * n * (p / q))
        for p in range(1, q + 1) if gcd(p, q) == 1
    ]
    c_q = sum(c_q)
    return np.real(c_q)


@memoize
def rs_matrix(N):
    """Return the ram sum matrix with normalization."""
    def inner(q, j):
        """Return the normalized ram sum for the coordinates."""
        return (1 / (phi(q) * N)) * ram_sum(1 + (j - 1) % q, q)

    return np.matrix([
        [inner(q, j) for j in range(1, N + 1)] for q in range(1, N + 1)
    ])


def seq_to_matrix(seq):
    """Return a four color indicator encoding of a sequence as a column 'vector'."""
    seq = seq.upper()
    return np.matrix([
        [1 if seqb == base else 0 for seqb in seq] for base in 'ACGT'
    ]).T


def seq_power_series(seq, RS=None):
    """Return a list with the ram power series for a seq."""
    if not RS:
        RS = rs_matrix(len(seq))
    seq = seq_to_matrix(seq)
    rft = abs(np.dot(RS, seq))
    power_series = np.sum(rft, axis=1)
    power_series = power_series[1:, 0].T.tolist()[0]  # Remove the first useless component
    return power_series


def power_series_sweep(seq, width=100, step=10):
    """Return a matrix with rows as power series of the given width."""
    RS = rs_matrix(width)
    windows = [(start, start + width) for start in range(0, len(seq), step)]
    mat = [seq_power_series(seq[start:end], RS=RS) for start, end in windows if end <= len(seq)]
    return np.matrix(mat)
