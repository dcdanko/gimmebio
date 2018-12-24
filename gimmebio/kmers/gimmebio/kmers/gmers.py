"""Tools for gallagher encoded kmers.

Gmers come in sets that cover a larger window.
The sets are cosntructed such that each base
in the larger window is covered exactly the
same number of times.
"""

import numpy as np

import gimmebio.seqs


class GmerBuilder:
    """Class to construct gmers of a given size froma givenb window size."""

    def __init__(self, inputK, outputK, posCov):
        self.inputK = inputK
        self.outputK = outputK
        self.posCov = posCov
        self.totalBlocks = posCov
        self.gmersPerBlock = inputK // outputK  # each block covers each position exactly once
        self.totalGmers = self.gmersPerBlock * posCov
        self._buildMatrix()

    def _buildMatrix(self):
        initBlock = np.zeros((self.gmersPerBlock, self.inputK))
        for gind in range(self.gmersPerBlock):
            for i in range(self.outputK):
                initBlock[gind, gind * self.outputK + i] = 1
        # initBlock is in the 'correct' format but we will need it transposed for permutations
        initBlock = initBlock.transpose()

        blocks = []
        for _ in range(self.totalBlocks):
            block = np.random.permutation(initBlock).transpose()
            blocks.append(block)
        mat = np.concatenate(blocks, axis=0)
        indexLists = [[]] * self.totalGmers
        for i, j in np.argwhere(mat > 0):
            indexLists[i].append(j)
        self.indexLists = indexLists

    def buildGmers(self, kmer):
        assert len(kmer) == self.inputK
        out = []
        for indList in self.indexLists:
            gmer = ''
            for ind in sorted(indList):
                gmer += kmer[ind]
            out.append(gmer)
        return out


class MinGmerSet:
    """Build gmers then take the one with the lowest numerical hash as a representative."""

    def __init__(self, K, W, seqs, pcov=8):
        self.K = K
        self.W = W
        self.gmerBuilder = GmerBuilder(W, K, pcov)
        self.nseqs = len(seqs)
        self.makeGmers(seqs)

    def makeGmers(self, seqs):
        self.kmers = {}
        for seq in seqs:
            kmers = gimmebio.seqs.makeCanonicalKmers(seq, len(seq), self.W)
            for kmer in kmers:
                gmers = self.gmerBuilder.buildGmers(kmer)
                gmers = [(gmer, hash(gmer)) for gmer in gmers]
                gmer = min(gmers, key=lambda x: x[1])
                self.kmers[gmer] = 1

    def getCount(self, kmer):
        """Return the count for a given gmer."""
        try:
            return self.kmers[kmer]
        except KeyError:
            return 0

    def overlap(self, other):
        """Return a list of kmers that occur in both sets."""
        assert isinstance(other, type(self))
        out = []
        for kmer in other:
            if kmer in self:
                out.append(kmer)
        return out

    def __contains__(self, kmer):
        return kmer in self.kmers

    def __iter__(self):
        return iter(self.kmers.keys())

    def withCounts(self):
        """Yield tuples of (kmer, count)."""
        return self.kmers.items()

    def __str__(self):
        out = sorted(self.kmers.keys())
        return ' '.join(out)

    def __len__(self):
        return len(self.kmers)
