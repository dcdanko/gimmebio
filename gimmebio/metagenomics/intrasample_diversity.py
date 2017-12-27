import pandas as pd
from scipy.spatial.distance import pdist, squareform
import numpy as np
import sys
import math
import argparse as ap

class LevelNotFoundException( Exception):
    pass

def checkLevel(taxon ,level):
    if level == 'species':
        return ('s__' in taxon) and ('t__' not in taxon)
    elif level == 'genus':
        return ('g__' in taxon) and ('s__' not in taxon)
    raise LevelNotFoundException()
    
def getSName(fName):
    return fName.split('/')[-1].split('.')[0]

class Sample:

    def __init__(self, sName, level):
        self.sName = sName
        self.level = level
        self.abunds = {}
        
    def addLine(self, line):
        taxon, abund = line.split()
        if checkLevel(taxon, self.level):
            self.abunds[taxon] = float(abund)

    @classmethod
    def parseMPA(ctype, mpaFile, level):
        sname = getSName(mpaFile)
        sample = Sample(sname, level)
        with open(mpaFile) as mF:
            for line in mF:
                sample.addLine(line)
        return sample

    def richness(self):
        return len( self.abunds)

    def shannonIndex(self):
        H = 0
        for count in self.abunds.values():
            p = count / sum(self.abunds.values())
            assert p <= 1
            H += p * math.log(p)
        if H < 0:
            H *= -1
        return H

def parseAggregator(agg):
    agger = {}
    with open(agg) as af:
        for line in af:
            pt, group = line.strip().split('\t')
            agger[pt] = group
    return agger

def noAgger(mpaFile, args):
    sample = Sample.parseMPA(mpaFile, args.level)
    line = sample.sName
    if args.use_richness:
        line += '\t{}'.format( sample.richness())
    if args.use_shannon:
        line += '\t{}'.format( sample.shannonIndex())
    print(line)

def withAgger(mpaFile, groups, agger, args):
    sName = getSName(mpaFile)
    try:
        gName = agger[sName]
    except KeyError:
        gName = sName
        
    try:
        group = groups[gName]
    except KeyError:
        group = Sample( gName, args.level)
        groups[gName] = group
    with open(mpaFile) as mF:
        for line in mF:
            group.addLine(line)

def printAgged(groups, args):
    for group in groups.values():
        line = group.sName
        if args.use_richness:
            line += '\t{}'.format( group.richness())
        if args.use_shannon:
            line += '\t{}'.format( group.shannonIndex())
        print(line)
        
    
def main():
    args = parseArgs()
    header = 'sample_name'
    if args.use_richness:
        header += '\trichness'
    if args.use_shannon:
        header += '\tshannon_index'
    print(header)

    agger = None
    if args.aggregator:
        agger = parseAggregator(args.aggregator)
        groups = {}
        
    for mpaFile in args.mpa_files:
        if not agger:
            noAgger(mpaFile, args)
        else:
            withAgger(mpaFile, groups, agger, args)
    if agger:
        printAgged(groups, args)
        
def  parseArgs():
    parser = ap.ArgumentParser()
    parser.add_argument('--aggregator', dest='aggregator',  default=None, help='Group files and calculate stats for the group')    
    parser.add_argument('--level', dest='level',  default='species', help='Taxa level to calculate at. Supports species, genus')
    parser.add_argument('--richness', dest='use_richness',action='store_true',help='Report richness')
    parser.add_argument('--shannon', dest='use_shannon',action='store_true',help='Report Shannon Index')
    parser.add_argument('mpa_files', nargs='+', help='Sample files')
    args = parser.parse_args()
    return args

    
if __name__ == '__main__':
    main()
