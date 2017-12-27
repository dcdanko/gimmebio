import pandas as pd
from scipy.spatial.distance import pdist, squareform
import numpy as np
import sys


def loadMatrix( mpaFiles):
    mapping = {}
    rowNames = []
    for mpaFile in mpaFiles:
        sname = mpaFile.split('/')[-1].split('.')[0]
        rowNames.append(sname)
        vec = {}
        with open(mpaFile) as mF:
            for line in mF:
                k, v = line.split()
                if ('f__' in k) and ('g__' not in k):
                    vec[k] = float(v)
        print('{} {}'.format(sname, vec.values()), file=sys.stderr)
        mapping[sname] = vec
    df = pd.DataFrame(mapping)
    sampleMatrix = df.transpose().fillna(value=0).as_matrix()

    # make each row sum to 1
    rowSums = sampleMatrix.sum(axis=1)
    sampleMatrix = sampleMatrix / rowSums[:, np.newaxis]
    
    return sampleMatrix, rowNames

def makeDistMatrix(sampleMatrix, rowNames, metric='cosine'):
    distm = pdist(sampleMatrix, metric=metric) 
    distm = squareform(distm)
    distm = pd.DataFrame( distm, columns=rowNames, index=rowNames)
    return distm

def main():
    mpaFiles = sys.argv[1:]
    sMatrix, rowNames = loadMatrix( mpaFiles)
    distm = makeDistMatrix( sMatrix, rowNames)
    out = distm.to_csv(sep='\t')
    sys.stdout.write(out)

if __name__ == '__main__':
    main()
