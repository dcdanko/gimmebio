from scipy.optimize import linprog
import numpy as np
import pandas as pd


class OptimizationFailedError(Exception):
    pass


def findTaxaAGSVec(proportions, sampleAGS, taxaBounds=True):
    nsamples, ntaxa = proportions.shape
    b = np.concatenate([sampleAGS, -1 * sampleAGS])
    if taxaBounds:
        taxaMax = 10 * 1000 * 1000
        taxaMin = 1000 * 1000
        b = np.concatenate([b,
                            -1 * taxaMin * np.ones(ntaxa),
                            taxaMax * np.ones(ntaxa)])
    c = np.concatenate([np.zeros(ntaxa), np.ones(nsamples)])
    A = np.bmat([[proportions, -1 * np.identity(nsamples)],
                 [-1 * proportions, -1 * np.identity(nsamples)]])
    if taxaBounds:
        A = np.bmat([[A],
                     [-1 * np.identity(ntaxa), np.zeros((ntaxa, nsamples))],
                     [np.identity(ntaxa), np.zeros((ntaxa, nsamples))]])
    res = linprog(c, A_ub=A, b_ub=b, method='interior-point')
    if not res.success:
        msg = ['Optimization terminated successfully',
               'Iteration limit reached',
               'Problem appears to be infeasible',
               'Problem appears to be unbounded']
        msg = msg[res.status]
        raise OptimizationFailedError(msg)
    taxaVec = res.x[:ntaxa]
    return taxaVec


def normalizeTaxa(proportions, sampleAGS, taxaBounds=False):
    taxaVec = findTaxaAGSVec(proportions, sampleAGS, taxaBounds=taxaBounds)
    normed = proportions / taxaVec
    taxaVec = pd.Series(taxaVec, index=proportions.columns)
    normed = pd.DataFrame(normed, index=proportions.index, columns=proportions.columns)
    return normed, taxaVec
