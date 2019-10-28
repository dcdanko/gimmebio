
from os.path import join, dirname

CUR_DIR = dirname(__file__)


def data_file(filename):
    """Return path to data dir."""
    return join(CUR_DIR, f'data/{filename}')


ECOLI_GENOME_FILENAME = data_file('e_coli.GCF_000005845.2_ASM584v2_genomic.fna')
ECOLI_GENE_ANNOTATION_FILENAME = data_file('e_coli.GCF_000005845.2_ASM584v2_feature_table.txt')

CACNES_GENOME_FILENAME = data_file('c_acnes.GCF_000008345.1_ASM834v1_genomic.fna')
CACNES_GENE_ANNOTATION_FILENAME = data_file('c_acnes.GCF_000008345.1_ASM834v1_feature_table.txt')

EXAMPLE_FASTQ = data_file('sample_fastq_zymo_control.fq')

MEGARES_FASTA = data_file('megares_database_v1.01.fasta')
