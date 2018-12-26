import gzip
import sys


def countAligned(alignfile):
    aligned = {}
    with gzip.open(alignfile) as af:
        for line in af:
            qid = line.split()[0]
            if qid not in aligned:
                aligned[qid] = True
    return len(aligned)

def main(args):
    if len(args) == 0:
        print("Usage: blast-tabular-file")
        return 1

    print(countAligned(args[0]))
    return 0

if __name__ == '__main__':
    main(sys.argv[1:])
