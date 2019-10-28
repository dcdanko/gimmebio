
import pandas as pd

from Bio import SeqIO

from .constants import (
    ECOLI_GENOME_FILENAME,
    ECOLI_GENE_ANNOTATION_FILENAME,
    CACNES_GENOME_FILENAME,
    CACNES_GENE_ANNOTATION_FILENAME,
    MEGARES_FASTA,
)


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


class ContigSet:

    def __init__(self):
        self.recs = []
        self.ids = []
        with open(self.genomic_fasta_file()) as faf:
            for rec in SeqIO.parse(faf, 'fasta'):
                self.contigs.append(rec)

    def seqs(self):
        return [rec.seq for rec in self.recs]

    def contig_fasta_file(self):
        raise NotImplementedError()


class MegaresContigs(ContigSet):

    def contig_fasta_file(self):
        return MEGARES_FASTA
