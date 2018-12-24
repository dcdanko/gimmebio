import argparse as ap



def median(dists):
    dists = sorted(dists)
    i = len(dists) // 2 
    if len(dists) % 2 == 0:
        return (dists[i-1] + dists[i] ) / 2
    return dists[i]

def parseAggregator(agg):
    agger = {}
    with open(agg) as af:
        for line in af:
            pt, group = line.strip().split('\t')
            agger[pt] = group
    return agger

def main():
    args = parseArgs()
    agger = parseAggregator(args.aggregator)
    tbl = {}
    with open(args.dists) as dF:
        for line in dF:
            a, b, d = line.strip().split()
            try:
                a = agger[a]
            except KeyError:
                pass
            try:
                b = agger[b]
            except KeyError:
                pass
            if a == b:
                continue
            d = float(d)
            try:
                tbl[a][b].append(d)
            except KeyError:
                try:
                    tbl[a][b] = [d]
                except KeyError:
                    tbl[a] = {b: [d]}
    for a in tbl.keys():
        for b, dists in tbl[a].items():
            d = median(dists)
            print('{}\t{}\t{}'.format(a,b,d))


def  parseArgs():
    parser = ap.ArgumentParser()
    parser.add_argument('--aggregator', dest='aggregator',  default=None, help='Group files and calculate stats for the group')
    parser.add_argument('--dists', dest='dists',  default=None, help='Long format distances to be aggregated')        
    args = parser.parse_args()
    return args

    
if __name__ == '__main__':
    main()
            
