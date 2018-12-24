import pandas as pd
import argparse as ap
import sys

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
        agger = {}
        with open(agg) as af:
            for line in af:
                pt, group = line.strip().split()
                agger[pt] = group
        return Aggregator(agger)

class ABRGroup:

    def __init__(self, name):
        self.name = name
        self.tbl = {}

    def add(self, abr, val):
        try:
            val = float(val)
            try:
                self.tbl[abr] += val
            except KeyError:
                self.tbl[abr] = val
        except ValueError:
            pass

def loadMatrix( abrFiles, agger):
    groups = {}
    for abrFile in abrFiles:
        sname = abrFile.split('/')[-1].split('.')[0]
        gname = agger[sname]
        try:
            group = groups[gname]
        except KeyError:
            group = ABRGroup(gname)
            groups[gname] = group
        with open(abrFile) as aF:
            for line in aF:
                k, v, = line.strip().split()[:2]
                group.add(k,v)
                
    df = { g.name: g.tbl for g in groups.values()}
    df = pd.DataFrame(df)
    df.fillna(value=0, inplace=True)
    df['rsum'] = df.sum(axis=1)
    df = df.sort_values(by='rsum', ascending=False).drop('rsum', axis=1)
    return df

def main():
    args = parseArgs()
    agger = Aggregator.parseAggregator( args.aggregator)
    abrs = loadMatrix( args.abrs, agger)
    out = abrs.to_csv(sep='\t')
    sys.stdout.write(out)

def  parseArgs():
    parser = ap.ArgumentParser()
    parser.add_argument('--aggregator', dest='aggregator',  default=None, help='Group files and calculate stats for the group')
    parser.add_argument('abrs', nargs='+', help='Files with ABR info (shortbred output)') 
    args = parser.parse_args()
    return args

    
if __name__ == '__main__':
    main()
