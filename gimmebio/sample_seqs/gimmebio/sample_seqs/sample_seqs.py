
from os.path import join, dirname
from Bio import SeqIO


def datadir(fname):
    return join(dirname(__file__), f'data/{fname}')


class EColiGenome:
    sequence_source_file = datadir('e_coli.GCF_000005845.2_ASM584v2_genomic.fna')

    def __init__(self):
        with open(EColiGenome.sequence_source_file) as faf:
            for rec in SeqIO.parse(faf, 'fasta'):
                self.seq = rec.seq
                break
