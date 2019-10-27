
import gimmebio.seqs


def make_kmers(seq, K, canon=True, gap=1):
    """Return a list of kmers in a sequence."""
    out = []
    for start in range(0, len(seq) - K + 1, gap):
        kmer = seq[start:start + K]
        if canon:
            kmer = gimmebio.seqs.canonical(kmer)
        out.append(kmer)
    return out


class KmerSet:
    """Represents the kmers in a read."""

    def __init__(self, Ks, seqs, canon=True, blockedKmers=None, allowedKmers=None):
        self.Ks = Ks
        if isinstance(self.Ks, int):
            self.Ks = [self.Ks]
        self.canon = canon
        self.nseqs = len(seqs)
        self.allowedKmers = allowedKmers
        self.blockedKmers = blockedKmers
        self.makeKmers(seqs)

    def makeKmers(self, seqs):
        """Add kmers to this set from a list of seqs."""
        self.kmers = {}
        for seq in seqs:
            for K in self.Ks:
                if self.canon:
                    kmers = gimmebio.seqs.makeCanonicalKmers(seq, len(seq), K)
                else:
                    kmers = make_kmers(seq, K, canon=False)
                for kmer in kmers:
                    if self.blockedKmers and kmer in self.blockedKmers:
                        continue
                    if self.allowedKmers and kmer not in self.allowedKmers:
                        continue
                    if kmer not in self.kmers:
                        self.kmers[kmer] = 0
                    self.kmers[kmer] += 1

    def getCount(self, kmer):
        """Return the number of times a kmer occurs."""
        if self.canon:
            kmer = gimmebio.seqs.canonical(kmer, len(kmer))
        if kmer in self.kmers:
            return self.kmers[kmer]
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
        if self.canon:
            kmer = gimmebio.seqs.canonical(kmer, len(kmer))
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
