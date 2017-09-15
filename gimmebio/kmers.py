import cseqs
from .seqs import *
import sys
import numpy as np
import click

################################################################################

class MinSparseKmerSet:
    '''
    Represents the kmers in a read
    '''
    def __init__(self, K, W, seqs, canonical=True):
        self.K = K
        self.W = W
        self.nseqs = len(seqs)
        self.makeKmers(seqs, canonical)
        
    def makeKmers(self, seqs, canonical):
        self.kmers = {}
        for seq in seqs:
            if canonical:
                kmers = cseqs.makeCanonicalKmers(seq, len(seq), self.K)
            else:
                kmers = cseqs.makeKmers(seq, len(seq), self.K)
            kmers = [(kmer, hash(kmer)) for kmer in kmers]
            kmersInWindow = self.W - self.K + 1
            numWindows =  len(kmers) - kmersInWindow + 1
            for windowStart in range( numWindows):
                window = kmers[windowStart:windowStart + kmersInWindow]

                if windowStart == 0:
                    # first window, minimum does not exist yet
                    minKmer = min(window,key=lambda x: x[1])
                    self.kmers[minKmer[0]] = 1 
                elif kmers[windowStart - 1][1] == minKmer[1]:
                    # the minimum has dropped out of the window
                    minKmer = min(window,key=lambda x: x[1])
                    self.kmers[minKmer[0]] = 1                     
                elif window[-1][1] < minKmer[1]:
                    # the new kmer is lower
                    minKmer = window[-1]
                    self.kmers[minKmer[0]] = 1                     
                    
                
                
                
    def getCount(self, kmer):
        try:
            return self.kmers[kmer]
        except KeyError:
            return 0

    def overlap(self, other):
        'Return a list of kmers that occur in both sets'
        
        assert type(other) == type(self)
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
        return self.kmers.items()
    
    def __str__(self):
        out = sorted( self.kmers.keys())
        return ' '.join(out)

    def __len__(self):
        return len(self.kmers)


class MinGmerSet:
    '''
    Represents the kmers in a read
    '''
    def __init__(self, K, W, seqs, pcov=8):
        self.K = K
        self.W = W
        self.gmerBuilder = GmerBuilder(W,K,pcov)
        self.nseqs = len(seqs)
        self.makeGmers(seqs)
        
    def makeGmers(self, seqs):
        self.kmers = {}
        for seq in seqs:
            kmers = cseqs.makeCanonicalKmers(seq, len(seq), self.W)
            for kmer in kmers:
                gmers = self.gmerBuilder.buildGmers(kmer)
                gmers = [(gmer, hash(gmer)) for gmer in gmers]
                gmer = min(gmers,key=lambda x: x[1])
                self.kmers[gmer]= 1
                
    def getCount(self, kmer):
        try:
            return self.kmers[kmer]
        except KeyError:
            return 0

    def overlap(self, other):
        'Return a list of kmers that occur in both sets'
        
        assert type(other) == type(self)
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
        return self.kmers.items()
    
    def __str__(self):
        out = sorted( self.kmers.keys())
        return ' '.join(out)

    def __len__(self):
        return len(self.kmers)


class GmerBuilder:

    def __init__(self, inputK, outputK, posCov):
        self.inputK = inputK
        self.outputK = outputK
        self.posCov = posCov
        self.totalBlocks = posCov
        self.gmersPerBlock = inputK // outputK # each block covers each position exactly once
        self.totalGmers = self.gmersPerBlock * posCov
        self._buildMatrix()

    def _buildMatrix(self):
        initBlock = np.zeros((self.gmersPerBlock, self.inputK))
        for gind in range(self.gmersPerBlock):
            for i in range(self.outputK):
                initBlock[gind, gind*self.outputK + i] = 1
        # initBlock is in the 'correct' format but we will need it transposed for permuations           
        initBlock = initBlock.transpose() 
                
        blocks = []
        for _ in range(self.totalBlocks):
            block = np.random.permutation(initBlock).transpose()
            blocks.append(block)
        mat = np.concatenate(blocks, axis=0)
        indexLists = [ [] ] *  self.totalGmers
        for i, j in np.argwhere( mat > 0):
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

    
class KmerSet:
    '''
    Represents the kmers in a read
    '''
    def __init__(self, Ks, seqs, canon=True, blockedKmers=None, allowedKmers=None):
        self.Ks = Ks
        if type(self.Ks) == int:
            self.Ks = [self.Ks]
        self.canon = canon
        self.nseqs = len(seqs)
        self.allowedKmers = allowedKmers
        self.blockedKmers = blockedKmers
        self.makeKmers(seqs)
        
    def makeKmers(self, seqs):
        self.kmers = {}
        for seq in seqs:
            for K in self.Ks:
                if self.canon:
                    #                kmers = makeKmers(seq, self.K)
                    kmers = cseqs.makeCanonicalKmers(seq, len(seq), K)
                else:
                    kmers = makeKmers(seq, K, canon=False)
                    #                kmers = cseqs.makeKmers(seq, len(seq), self.K)
                for kmer in kmers:
                    if self.blockedKmers and kmer in self.blockedKmers:
                        continue
                    if self.allowedKmers and kmer not in self.allowedKmers:
                        continue
                    if kmer not in self.kmers:
                        self.kmers[kmer] = 0
                    self.kmers[kmer] += 1
#        self.kmerKeys = sorted( self.kmers.keys())
                
    def getCount(self, kmer):
        if self.canon:
            kmer = cseqs.canonical(kmer, len(kmer))
#            kmer = canonical(kmer)
        if kmer in self.kmers:
            return self.kmers[kmer]
        return 0

    def overlap(self, other):
        'Return a list of kmers that occur in both sets'
        
        assert type(other) == type(self)
        out = []
        for kmer in other:
            if kmer in self:
                out.append(kmer)
        return out
        '''
        
        i, ourKmers, iMax = 0, self.kmerKeys, len(self.kmerKeys)
        j, theirKmers, jMax = 0, other.kmerKeys, len(other.kmerKeys)
        out = []
        while i < iMax and j < jMax:
            ourKmer = ourKmers[i]
            theirKmer = theirKmers[j]
            if ourKmer < theirKmer:
                i += 1
            elif theirKmer < ourKmer:
                j += 1
            else:
                i += 1
                j += 1
                out.append(ourKmer)
        return out
        '''
        
    
    def __contains__(self, kmer):
        if self.canon:
            kmer = cseqs.canonical(kmer, len(kmer))
#            kmer = canonical(kmer)
            
        return kmer in self.kmers

    def __iter__(self):
        return iter(self.kmers.keys())

    def withCounts(self):
        return self.kmers.items()
    
    def __str__(self):
        out = sorted( self.kmers.keys())
        return ' '.join(out)

    def __len__(self):
        return len(self.kmers)
    
class RabinKmerSet:
    def __init__(self, seqs, P=5, canon=True, radix=13, initTblSize=1000):
        self.P = P
        self.K = 1 + (2**self.P)
        self.canon = canon
        self.masterTbl = [[]]*initTblSize
        self.radix = radix
        self.makeKmers(seqs)
        self.nseqs = len(seqs)
        self.lCutoff = 10

    def makeKmers(self, seqs):
        for seqNum, seq in enumerate(seqs):
            for kmer, rHash in ckmers.rabinFingerprints(seq,
                                                        len(seq),
                                                        self.P,
                                                        self.radix):
                rHash %= len(self.masterTbl)
                added = False
                tbl = self.masterTbl[rHash]
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
                            self.masterTbl[rHash] = {kmer: count for kmer, count in tbl}

        
    def getCount(self, kmer, norecurse=False):
        count = 0
        rHash = 0
        for i, base in enumerate(kmer):
            power = self.K-(i+1)
            rHash += baseToInt(base) * (self.radix ** power)

        t = self.masterTbl[rHash]
        if type(t) is dict:
            if kmer in t:
                count += t[kmer]
        else:
            for storedKmer, kCount in t:
                if kmer == storedKmer:
                    count += kCount

        if self.canon and not norecurse:
            count += self.getCount( cseqs.reverseComplement(kmer, len(kmer)), norecurse=True)
        return count

    def getOverlappingKmerCounts(self, other):
        assert type(other) == type(self)
        kmerCounts = {} # keys are kmers, values are the number of times they occur in each
        def countKmer(kmer):
            if kmer in kmerCounts:
                kmerCounts[kmer] += 1
            else:
                kmerCounts[kmer] = 1
            
        for i, myTbl in enumerate(self.tbl):
#            print('my_table: {} {}'.format(i, myTbl))
            if len(myTbl) == 0:
                continue

            theirTbl = other.tbl[i]
            if len(theirTbl) == 0:
                continue
            print('length_my_table: {}, length_their_table: {}'.format(len(myTbl), len(theirTbl)))

            myTblIter = myTbl
            if type(myTbl) == dict:
                myTblIter = myTbl.items()
                
            if type(theirTbl) == dict:
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
            if type(tbl) is dict:
                for kmer in tbl.keys():
                    yield kmer
            else:
                for kmer, count in tbl:
                    yield kmer
        
    
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



def makeKmers(seq, K, canon=True):
    out = []
    for start in range(len(seq)-K+1):
        kmer = seq[start:start+K]
        if canon:
            kmer = canonical(kmer)
        out.append(kmer)
    
    return out

@click.command()
@click.option('-k', '--kmer-len', default=32, help='Length of kmers')
@click.option('--canonical/--non-canonical', default=False, help='Canonicalize kmers')
def makeKmers_CLI(kmer_len, canonical):
    for line in sys.stdin:
        seq = line.strip()
        if canonical:
            kmers = cseqs.makeCanonicalKmers(seq, len(seq), kmer_len)
        else:
            kmers = cseqs.makeKmers(seq, len(seq), kmer_len)
        for kmer in kmers:
            print(kmer)

        
if __name__ == '__main__':
    makeKmers_CLI()
