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
            try:
                self.abunds[taxon] += float(abund)
            except KeyError:
                self.abunds[taxon] = float(abund)
                
    @classmethod
    def parseMPA(ctype, mpaFile, level):
        sname = getSName(mpaFile)
        sample = Sample(sname, level)
        with open(mpaFile) as mF:
            for line in mF:
                sample.addLine(line)
        return sample

    def topN(self, n):
        abunds = [ (k,v) for k,v in self.abunds.items()]
        abunds = sorted( abunds, key=lambda x: x[1], reverse=True)
        abunds = abunds[:n]
        return {k:v for k,v in abunds}

def noAgger(mpaFile, processed, args):
    sample = Sample.parseMPA(mpaFile, args.level)
    if args.top_n > 0:
        processed[sample.sName] = sample.topN( args.top_n)

    
def parseAggregator(agg):
    agger = {}
    with open(agg) as af:
        for line in af:
            pt, group = line.strip().split('\t')
            agger[pt] = group
    return agger


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

def processAgged(groups, processed, args):
    for group in groups.values():
        if args.top_n > 0:
            processed[group.sName] = group.topN( args.top_n)
    
def main():
    args = parseArgs()

    if args.aggregator:
        agger = parseAggregator(args.aggregator)
        groups = {}
        
    processed = {}
    for mpaFile in args.mpa_files:
        if not agger:
            noAgger(mpaFile, processed, args)
        else:
            withAgger(mpaFile, groups, agger, args)
    if agger:
        processAgged(groups, processed, args)

    df = pd.DataFrame(processed)
    df.fillna(value=0, inplace=True)
    sys.stdout.write(df.to_csv(sep='\t'))
        
def  parseArgs():
    parser = ap.ArgumentParser()
    parser.add_argument('--level', dest='level',  default='species', help='Taxonomic level to use: species, genus')        
    parser.add_argument('--aggregator', dest='aggregator',  default=None, help='Group files and calculate stats for the group')    
    parser.add_argument('--top-n', dest='top_n',  default=-1, type=int, help='Get the first N most abundant species')
    parser.add_argument('mpa_files', nargs='+', help='Sample files')
    args = parser.parse_args()
    return args

    
if __name__ == '__main__':
    main()
