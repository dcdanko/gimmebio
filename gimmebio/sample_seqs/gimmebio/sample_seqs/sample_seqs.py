
import pandas as pd
import random

from Bio import SeqIO

from .constants import (
    ECOLI_GENOME_FILENAME,
    ECOLI_GENE_ANNOTATION_FILENAME,
    CACNES_GENOME_FILENAME,
    CACNES_GENE_ANNOTATION_FILENAME,
    SAUREUS_GENOME_FILENAME,
    SAUREUS_GENE_ANNOTATION_FILENAME,
    MEGARES_FASTA,
)


def sim_one(contig, l, g):
    pos = random.randint(0, len(contig) - 2 * l - g - 1)
    r1 = contig[pos:pos + l]
    r2 = contig[pos + l + g:pos + l + g + l]

    def add_errs(seq, e):
        new_seq = ''
        for base in seq:
            if random.random() > e:
                new_seq += base
                continue
            new_seq += random.choice('ACGT')
        return new_seq

    return add_errs(r1, 0.01), add_errs(r2, 0.01)


class BacterialGenome:

    def __init__(self):
        self.contigs = []
        with open(self.genomic_fasta_file()) as faf:
            for rec in SeqIO.parse(faf, 'fasta'):
                self.contigs.append(rec.seq)
        self.contigs = sorted(self.contigs, key=lambda el: -len(el))
        self.annotations = pd.read_table(self.genomic_annotation_file(), header=0)

    def longest_contig(self):
        return self.contigs[0]

    def genomic_fasta_file(self):
        raise NotImplementedError()

    def genomic_annotation_file(self):
        raise NotImplementedError()

    def sim_reads(self, N, l=150, max_pos=1000000000000):
        longtig = str(self.contigs[0])
        max_pos = min(len(longtig), max_pos)
        longtig = longtig[:max_pos]
        for _ in range(N):
            yield sim_one(longtig, l, g=400)


class EcoliGenome(BacterialGenome):

    def genomic_fasta_file(self):
        return ECOLI_GENOME_FILENAME

    def genomic_annotation_file(self):
        return ECOLI_GENE_ANNOTATION_FILENAME


class CacnesGenome(BacterialGenome):

    def genomic_fasta_file(self):
        return CACNES_GENOME_FILENAME

    def genomic_annotation_file(self):
        return CACNES_GENE_ANNOTATION_FILENAME


class SaureusGenome(BacterialGenome):

    def genomic_fasta_file(self):
        return SAUREUS_GENOME_FILENAME

    def genomic_annotation_file(self):
        return SAUREUS_GENE_ANNOTATION_FILENAME


class ContigSet:

    def __init__(self):
        self.recs = []
        with open(self.contig_fasta_file()) as faf:
            for rec in SeqIO.parse(faf, 'fasta'):
                self.recs.append(rec)

    def seqs(self):
        return [rec.seq for rec in self.recs]

    def contig_fasta_file(self):
        raise NotImplementedError()


class MegaresContigs(ContigSet):

    def contig_fasta_file(self):
        return MEGARES_FASTA


class VanAContigs(ContigSet):

    def __init__(self):
        super().__init__()
        self.recs = [rec for rec in self.recs if '|VANA' in rec.id]

    def contig_fasta_file(self):
        return MEGARES_FASTA
