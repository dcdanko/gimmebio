import pandas as pd
from scipy.spatial.distance import pdist, squareform
import numpy as np
import sys
import argparse as ap

class LevelNotFoundException( Exception):
    pass

def checkLevel(taxon ,level):
    if level is None:
        return taxon
    if level == 'species':
        return ('s__' in taxon) and ('t__' not in taxon)
    elif level == 'genus':
        return ('g__' in taxon) and ('s__' not in taxon)
    raise LevelNotFoundException()

def anyIn(taxon, els):
    if (els is None) or (len(els) == 0):
        return True
    for el in els:
        if el.lower() in taxon.lower():
            return True
    return False

class Aggregator:
    def __init__(self, agg):
        self.agg = agg

    def __getitem__(self, key):
        try:
            return self.agg[key]
        except KeyError:
            return key

    @staticmethod
    def parseAggregator(agg):
        if agg == None:
            return Aggregator({})
        agger = {}
        with open(agg) as af:
            for line in af:
                pt, group = line.strip().split()
                agger[pt] = group
        return Aggregator(agger)

def parseTaxa(taxaf):
    if taxaf is None:
        return []
    out = []
    with open(taxaf) as tf:
        for line in tf:
            out.append(line.strip())
    return out
    
class SpeciesGroup:
    def __init__(self, name, level, taxa):
        self.name = name
        self.tbl = {}
        self.level = level
        self.taxa = taxa
        
    def add(self, abr, val):
        try:
            val = float(val)
            if checkLevel(abr, self.level) and anyIn(abr, self.taxa):
                try:
                    self.tbl[abr] += val
                except KeyError:
                    self.tbl[abr] = val
        except ValueError:
            pass
        

def loadMatrix( mpaFiles, agger, level, taxa, normalize):
    groups = {}
    for mpaFile in mpaFiles:
        sname = mpaFile.split('/')[-1].split('.')[0]
        gname = agger[sname]
        try:
            group = groups[gname]
        except KeyError:
            group = SpeciesGroup(gname, level, taxa)
            groups[gname] = group

        with open(mpaFile) as mF:
            for line in mF:
                k, v = line.split()
                group.add(k,v)
                
    df = { g.name: g.tbl for g in groups.values()}
    df = pd.DataFrame(df)
    df.fillna(value=0,inplace=True)
    if normalize:
        df = df.transpose()
        df /= df.sum()
        df = df.transpose()
    return df

def main():
    args = parseArgs()
    agger = Aggregator.parseAggregator( args.aggregator)
    taxa = parseTaxa( args.taxa)
    species = loadMatrix( args.mpas, agger, args.level, taxa, not args.no_normal)
    out = species.to_csv(sep='\t')
    sys.stdout.write(out)

def  parseArgs():
    parser = ap.ArgumentParser()
    parser.add_argument('-a','--aggregator', dest='aggregator',  default=None, help='Group files and calculate stats for the group')
    parser.add_argument('mpas', nargs='+', help='MPA Files with species info')
    parser.add_argument('-l','--level', dest='level',  default=None, help='Taxa level to calculate at. Supports species, genus')
    parser.add_argument('--no-normal', dest='no_normal', action='store_true', help='Do not make columns sum to 1')
    parser.add_argument('-t','--taxa', dest='taxa',  default=None, help='Taxa list. Only include taxa from this list.')
    args = parser.parse_args()
    return args

    
if __name__ == '__main__':
    main()
