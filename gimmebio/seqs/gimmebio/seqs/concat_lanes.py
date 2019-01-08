import subprocess as sp
from sys import argv


def getSname(fname):
    return fname.split('/')[-1].split('_L')[0]


def getLane(fname):
    return int(fname.split('/')[-1].split('L00')[1].split('_')[0])


def getRead(fname):
    return int(fname.split('/')[-1].split('R')[1].split('_')[0])


tups = {}
for fname in argv[1:]:
    key = (getSname(fname), getRead(fname))
    try:
        tups[key]
    except KeyError:
        tups[key] = {}
    tups[key][getLane(fname)]  = fname

for (sname, read), val in tups.items():
    a = val[1]
    b = val[2]
    out = 'concat_new/{}_R{}.fq.gz'.format(sname, read)
    cmd = 'zcat {} {} | gzip > {}'.format(a, b, out)
    print(cmd)
    sp.call(cmd, shell=True)
