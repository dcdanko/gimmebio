
import numpy as np


def text_scatter_plot(values, graph_width=80, graph_height=30):
    """Return a string representation of a scatter plot of values."""
    out_str = ''
    minX, maxX = min([el[0] for el in values]), max([el[0] for el in values])
    minY, maxY = min([el[1] for el in values]), max([el[1] for el in values])

    xBinWidth = (0.00001 + maxX - minX) / graph_width
    yBinWidth = (0.00001 + maxY - minY) / graph_height
    graph = np.zeros((graph_height, graph_width))

    values = sorted(values)
    for x, y in values:
        xInd = int((x - minX) // xBinWidth)
        yInd = int((y - minY) // yBinWidth)
        graph[(graph_height - 1 - yInd), xInd] += 1

    nonZeroGraph = np.squeeze(graph)
    nonZeroGraph = nonZeroGraph[nonZeroGraph > 0]
    firstQ = np.percentile(nonZeroGraph, 25)
    secondQ = np.percentile(nonZeroGraph, 50)
    thirdQ = np.percentile(nonZeroGraph, 75)
    outs = []
    longestDimStr = 0
    for i in range(graph_height):
        sval = ''
        for j in range(graph_width):
            val = graph[i, j]
            if val == 0:
                sval += ' '
            elif val >= thirdQ:
                sval += 'O'
            elif val >= secondQ:
                sval += '*'
            else:
                sval += 'o'
        yBin = graph_height - i
        dimStr = '[{:.2f}, {:.2f}) '.format(
            yBin * yBinWidth + minY,
            (yBin + 1) * yBinWidth + minY
        )
        if len(dimStr) > longestDimStr:
            longestDimStr = len(dimStr)
        outs.append((dimStr, sval))

    out_str += 'o == (0, {}]\n'.format(firstQ)
    out_str += '* == ({}, {}]\n'.format(firstQ, secondQ)
    out_str += 'O == ({}, {}]\n'.format(thirdQ, np.amax(graph))

    haxis = ' ' * longestDimStr + '.' * (graph_width + 4)
    out_str += haxis + '\n'
    for dimStr, disp in outs:
        dimStr += ' ' * (longestDimStr - len(dimStr))
        out_str += '{}. {} .\n'.format(dimStr, disp)
    out_str += haxis + '\n'

    sval = ' ' * longestDimStr
    maxS = '{}'.format(maxX)
    minS = '{}'.format(minX)
    sval += minS + ' ' * (graph_width + 4 - len(maxS) - len(minS))
    sval += maxS
    out_str += sval + '\n'

    return out_str
