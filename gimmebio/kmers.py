import ckmers
from .seqs import *
import sys

################################################################################

class KmerSet:
    '''
    Represents the kmers in a read
    '''
    def __init__(self, K, seqs, canon=True):
        self.K = K
        self.canon = canon
        self.makeKmers(seqs)
        self.nseqs = len(seqs)

        
    def makeKmers(self, seqs):
        self.kmers = {}
        for seq in seqs:
            for i in range(len(seq) - self.K + 1):
                start = i
                end = i+self.K
                kmer = seq[start:end]
                if self.canon:
                    kmer = canonical(kmer)
                if kmer not in self.kmers:
                    self.kmers[kmer] = 0
                self.kmers[kmer] += 1

    def getCount(self, kmer):
        if self.canon:
            kmer = canonical(kmer)
        if kmer in self.kmers:
            return self.kmers[kmer]
        return 0

    def __iter__(self):
        return iter(self.kmers.keys())

class RabinKmerSet:
    def __init__(self, seqs, P=5, canon=True, radix=13, initTblSize=1000):
        self.P = P
        self.K = 1 + (2**self.P)
        self.canon = canon
        self.tbl = [[]]*initTblSize
        self.radix = radix
        self.makeKmers(seqs)
        self.lCutoff = 5

    def makeKmers(self, seqs):
        for seqNum, seq in enumerate(seqs):
            for kmerStart, rHash in enumerate( ckmers.rabinFingerprints(seq,
                                                                        len(seq),
                                                                        self.P,
                                                                        self.radix)):
                rHash %= len(self.tbl)
                added = False
                kmer = seq[kmerStart: kmerStart + self.K]
                tbl = self.tbl[rHash]
                if type(tbl) is dict:
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
                            tbl.append( [kmer,1])
                            if len(tbl) > self.lCutoff:
                                self.tbl[rHash] = {kmer: count for kmer, count in tbl}

        
    def getCount(self, kmer, norecurse=False):
        count = 0
        rHash = 0
        for i, base in enumerate(kmer):
            power = self.K-(i+1)
            rHash += baseToInt(base) * (self.radix ** power)

        t = self.tbl[rHash]
        if type(t) is dict:
            if kmer in t:
                return t[kmer]
        else:
            for storedKmer, kCount in t:
                if kmer == storedKmer:
                    count += kCount

        if self.canon and not norecurse:
            count += self.getCount( reverseComplement(kmer), norecurse=True)
        return count
                

        
    
################################################################################



def rabinFingerprints(seq, k, prime=7, modulo=None):
    initSeq = seq[:k]

    initHash = 0
    for i, base in enumerate(initSeq):
        power = k-(i+1)
        initHash += baseToInt(base) * (prime ** power)

    hashes = [ [initSeq, initHash]]
    if modulo is not None:
        hashes[0][1] %= modulo

    oldHash = initHash
    oldSeq = initSeq
    maxPower = prime ** (k - 1)
    for base in seq[k:]:
        nextSeq = oldSeq[1:] + base        
        nextHash = prime * (oldHash - baseToInt(oldSeq[0]) * maxPower)
        nextHash += baseToInt(base)
        hashes.append( [nextSeq, nextHash])
        if modulo is not None:
            hashes[-1][1] %= modulo
        oldHash, oldSeq = nextHash, nextSeq

    return hashes
        
