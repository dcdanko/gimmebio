import click

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
                pt, group = line.strip().split('\t')
                agger[pt] = group
        return Aggregator(agger)


def loadMatrix( fileToAgg, agger):
    groups = {}
    with open(fileToAgg) as f:
        for line in f:
            tkns = line.strip().split()
            key, val = tkns[:2]
            val = int(val)
            key = agger[key]
            try:
                groups[key][0] += 1
                groups[key][1] += val
            except KeyError:
                groups[key] = [1, val]
    return groups

@click.command()
@click.argument('data')
@click.argument('agger')
def main(data, agger):
    agger = Aggregator.parseAggregator(agger)
    groups = loadMatrix( data, agger)
    for k, (n, v) in groups.items():        
        print('{}\t{}'.format(k,v/n))

    
if __name__ == '__main__':
    main()
