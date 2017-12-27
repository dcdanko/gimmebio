import sys

def cleanName(name):
    name = name.split('/')[-1]
    name = name.split('.')[0]
    return name


def main():
    mashF = sys.argv[1]
    with open(mashF) as mF:
        for line in mF:
            line = line.strip().split()
            a = cleanName(line[0])
            b = cleanName(line[1])
            d = float(line[2])
            print('{}\t{}\t{}'.format(a,b,d))
