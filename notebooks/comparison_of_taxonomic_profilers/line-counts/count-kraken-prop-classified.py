import gzip
import sys
import subprocess as sp
import numpy as np

def countAligned(cinfile):
    species = cinfile.split('/')[-1].split('.')[1].split('-')[0].split('_')[0]
    root = cinfile[5:]
    root = root[: root.index('.classified.tsv.gz')]
    linecountfile = 'lines_in.' + root + '.fastq.gz'
    try:
        with open(cinfile) as c:
            C = int(c.read().strip())
        with open(linecountfile) as l:
            L = int(l.read().strip())
        P = C / (L / 4.0)
        return (species, P)
    except:
        return False



def mergeAligned(outputs):
    merged = {}
    for species, out in outputs:
        if species not in merged:
            merged[species] = []
        merged[species].append(out)
    return merged

    

def crunchAligned(merged):
    crunched = {}
    for sp, vals in merged.items():
        u = np.mean(vals)
        sd = np.std(vals)
        crunched[sp] = (u,sd)
    return crunched

def prettyprint(crunched):
    print("\n--------------------------------------------------------\n")
    outline = "{:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t& {:.1f} ({:.1f}) \t\\\\"
    for row in crunched.itertuples():
        print(row)
        ar = []
        for v in row[1:]:
            print(v)
            ar.append(float(v[0]))
            ar.append(float(v[1]))
        print(ar)
        print(outline.format(*ar))
        
    
def main(args):
    if len(args) == 0:
        print("Usage: cin-files")
        return 1

    outputs = []
    for f in args:
        a = countAligned(f)
        if not a:
            continue
        outputs.append(a)
    
    merged = mergeAligned(outputs)
    crunched = crunchAligned(merged)
    for k,v in crunched.items():
        print("{} : {}".format(k,v))
    
if __name__ == '__main__':
    main(sys.argv[1:])
