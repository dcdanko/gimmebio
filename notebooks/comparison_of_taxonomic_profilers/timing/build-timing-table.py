import gzip
import sys
import subprocess as sp
import numpy as np

def countAligned(tfile):
    tool = tfile.split('.')[-2]
    lfile = '.'.join(tfile.split('.')[:-2])
    if lfile.endswith('.fa.gz'):
        lfile = lfile[:lfile.index('.fa.gz')]

    lfile = '../line-counts/lines_in.' + lfile +'.fastq.gz'
    try:
        with open(tfile) as t:
            for line in t:
                if 'command exited' in line.lower():
                    return False
                elif 'user time' in line.lower():
                    U = float(line.split(':')[1])
                elif 'system time' in line.lower():
                    S = float(line.split(':')[1])   
        with open(lfile) as l:
            N = int(l.read().strip())/4

        T = 1000*1000*float(U + S)/N
        return (tool,T)
    except Exception as e:
        print("{} {}".format(tfile,e))
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
        n = len(vals)
        crunched[sp] = (u,sd,n)
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
        print("Usage: timing-files")
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
