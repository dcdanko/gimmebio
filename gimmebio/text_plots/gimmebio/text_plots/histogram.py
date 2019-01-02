
from math import log


def text_histogram(values, logy=False, max_pos=None, bin_width=1, graph_width=70):
    """Return a string representation of a histogram of values."""
    out_str, values = '', sorted(values)
    binned = {}
    for el in values:
        binned[el // bin_width] = 1 + binned.get(el // bin_width, 0)

    if max_pos is not None:
        out_str += '# Clipping X-Axis at {:,}\n'.format(max_pos)
        binned = {k: v for k, v in binned.items() if (k * bin_width) <= max_pos}
    if logy:
        binned = {k: log(v) for k, v in binned.items()}

    minBin, maxBin = int(min(binned.keys())), int(max(binned.keys()) + 0.5)
    maxVal = max(binned.values())
    mult = graph_width / maxVal

    out_str += 'Max: {}\n'.format(maxVal)
    maxHeader, bin_values = 0, []
    for i in range(minBin, maxBin + 1):
        val = binned.get(i, 0)
        sval = ['='] * int(val * mult)
        if len(sval) == 0 and val > 0:
            sval = '.'
        else:
            sval = ''.join(sval)
        header = '[{:.2f}, {:.2f}) {}'.format(i * bin_width, (i + 1) * bin_width, int(val))
        if len(header) > maxHeader:
            maxHeader = len(header)
        bin_values.append((header, sval))

    for header, sval in bin_values:
        spacer = ' ' * (maxHeader - len(header))
        out_str += '{}{} : {}\n'.format(header, spacer, sval)
    return out_str
