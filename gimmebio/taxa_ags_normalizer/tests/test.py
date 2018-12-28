from taxon_normalizer.normalizer import normalizeTaxa
import numpy as np


def simple_test():
    P = np.matrix([[1 / 3, 1 / 3, 1 / 3],
                   [1 / 4, 1 / 4, 1 / 2]])
    S = np.array([2, 2.25])
    N, T = normalizeTaxa(P, S)
    print(T)
    print(N)

if __name__ == '__main__':
    simple_test()