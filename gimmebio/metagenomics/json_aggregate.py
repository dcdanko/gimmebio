import click
import json
import pandas as pd
import os.path

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


def loadMatrix( jsons, agger):
    groups = {}
    for jsonFile in jsons:
        sname = os.path.basename(jsonFile).split('.')[0]
        j = json.loads( open(jsonFile).read())
        j = {k: float(v) for k,v in j.items()}
        key = agger[sname]
        try:
            groups[key][0] += 1
            for k   in groups[key][1].keys():
                groups[key][1][k] += j[k]
        except KeyError:
            groups[key] = [1, j]
    tbl = {}
    for key, (count, j) in groups.items():
        n = {}
        for k, v in j.items():
            n[k] = v / count
        tbl[key] = n
    tbl = pd.DataFrame(tbl)
    print(tbl.to_csv())

@click.command()
@click.argument('agger')
@click.argument('jsons', nargs=-1)
def main(agger, jsons):
    agger = Aggregator.parseAggregator(agger)
    loadMatrix( jsons, agger)

    
if __name__ == '__main__':
    main()
