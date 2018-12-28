"""Tools for Minimum Sparse Kmers.

Minimum sparse kmers take a window and fingerprint
it by finding the kmer (of given size) with the
smallest numerical hash within the window. Since
adjacent windows share most of their kmers they
are likely to share the same fingerprint.
"""

import gimmebio.seqs


class MinSparseKmerSet:
    """Represents the minsparse kmers in a read."""

    def __init__(self, K, W, seqs, canonical=True):
        self.K = K
        self.W = W
        self.nseqs = len(seqs)
        self.makeKmers(seqs, canonical)

    def makeKmers(self, seqs, canonical):
        self.kmers = {}
        for seq in seqs:
            if canonical:
                kmers = gimmebio.seqs.makeCanonicalKmers(seq, len(seq), self.K)
            else:
                kmers = gimmebio.seqs.makeKmers(seq, len(seq), self.K)
            kmers = [(kmer, hash(kmer)) for kmer in kmers]
            kmersInWindow = self.W - self.K + 1
            numWindows = len(kmers) - kmersInWindow + 1
            for windowStart in range(numWindows):
                window = kmers[windowStart:windowStart + kmersInWindow]

                if windowStart == 0:
                    # first window, minimum does not exist yet
                    minKmer = min(window, key=lambda x: x[1])
                    self.kmers[minKmer[0]] = 1
                elif kmers[windowStart - 1][1] == minKmer[1]:
                    # the minimum has dropped out of the window
                    minKmer = min(window, key=lambda x: x[1])
                    self.kmers[minKmer[0]] = 1
                elif window[-1][1] < minKmer[1]:
                    # the new kmer is lower
                    minKmer = window[-1]
                    self.kmers[minKmer[0]] = 1

    def getCount(self, kmer):
        """Return the number of times a kmer occurs in this set."""
        try:
            return self.kmers[kmer]
        except KeyError:
            return 0

    def overlap(self, other):
        """Return a set of the kmers that occur in both sets."""
        assert isinstance(other, type(self))
        out = set()
        for kmer in other:
            if kmer in self:
                out.add(kmer)
        return out

    def remove(self, kmer):
        """Remove a kmer from this set."""
        del self.kmers[kmer]

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
