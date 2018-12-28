"""Rabin Kmers.

This has something to do with rabin-karp rolling hashes
but I don't remember why I was interested in this.
"""

import gimmebio.seqs


def rabinFingerprints(seq, k, prime=7, modulo=None):
    initSeq = seq[:k]

    initHash = 0
    for i, base in enumerate(initSeq):
        power = k - (i + 1)
        initHash += gimmebio.seqs.baseToInt(base) * (prime ** power)

    hashes = [[initSeq, initHash]]
    if modulo is not None:
        hashes[0][1] %= modulo

    oldHash = initHash
    oldSeq = initSeq
    maxPower = prime ** (k - 1)
    for base in seq[k:]:
        nextSeq = oldSeq[1:] + base
        nextHash = prime * (oldHash - gimmebio.seqs.baseToInt(oldSeq[0]) * maxPower)
        nextHash += gimmebio.seqs.baseToInt(base)
        hashes.append([nextSeq, nextHash])
        if modulo is not None:
            hashes[-1][1] %= modulo
        oldHash, oldSeq = nextHash, nextSeq

    return hashes


class RabinKmerSet:
    def __init__(self, seqs, P=5, canon=True, radix=13, initTblSize=1000):
        self.P = P
        self.K = 1 + (2**self.P)
        self.canon = canon
        self.masterTbl = [[]] * initTblSize
        self.radix = radix
        self.makeKmers(seqs)
        self.nseqs = len(seqs)
        self.lCutoff = 10

    def makeKmers(self, seqs):
        for seqNum, seq in enumerate(seqs):
            for kmer, rHash in rabinFingerprints(seq, len(seq), self.P, self.radix):
                rHash %= len(self.masterTbl)
                added = False
                tbl = self.masterTbl[rHash]
                if isinstance(tbl, dict):
                    if kmer in tbl:
                        tbl[kmer] += 1
                    else:
                        tbl[kmer] = 1
                else:
                    for i, (storedKmer, count) in enumerate(tbl):
                        if kmer == storedKmer:
                            tbl[i][1] += 1
                            added = True
                            break
                    if not added:
                        tbl.append([kmer, 1])
                        if len(tbl) > self.lCutoff:
                            self.masterTbl[rHash] = {kmer: count for kmer, count in tbl}

    def getCount(self, kmer, norecurse=False):
        count, rHash = 0, 0
        for i, base in enumerate(kmer):
            power = self.K - (i + 1)
            rHash += gimmebio.seqs.baseToInt(base) * (self.radix ** power)

        t = self.masterTbl[rHash]
        if isinstance(t, dict):
            if kmer in t:
                count += t[kmer]
        else:
            for storedKmer, kCount in t:
                if kmer == storedKmer:
                    count += kCount

        if self.canon and not norecurse:
            count += self.getCount(gimmebio.seqs.reverseComplement(kmer, len(kmer)), norecurse=True)
        return count

    def getOverlappingKmerCounts(self, other):
        assert isinstance(other, type(self))
        kmerCounts = {}  # keys are kmers, values are the number of times they occur in each

        def countKmer(kmer):
            if kmer in kmerCounts:
                kmerCounts[kmer] += 1
            else:
                kmerCounts[kmer] = 1

        for i, myTbl in enumerate(self.tbl):
            if not myTbl:
                continue

            theirTbl = other.tbl[i]
            if not theirTbl:
                continue
            print('length_my_table: {}, length_their_table: {}'.format(len(myTbl), len(theirTbl)))

            myTblIter = myTbl
            if isinstance(myTbl, dict):
                myTblIter = myTbl.items()

            if isinstance(theirTbl, dict):
                for kmer, myCount in myTblIter:
                    if kmer in theirTbl:
                        countKmer(kmer)
            else:
                for kmer, myCount in myTblIter:
                    for theirKmer, theirCount in theirTbl:
                        if kmer == theirKmer:
                            countKmer(kmer)
                            break
        return len(kmerCounts.keys()), kmerCounts

    def __iter__(self):
        for tbl in self.tbl:
            if isinstance(tbl, dict):
                for kmer in tbl.keys():
                    yield kmer
            else:
                for kmer, count in tbl:
                    yield kmer
