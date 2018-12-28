
from os.path import join, dirname

TEST_DIR = dirname(__file__)

def from_here(subpath):
    return join(TEST_DIR, subpath)


FASTQ_FILEPATH = from_here('test_data/sample_reads.fq')
BED_FILEPATH = from_here('test_data/sample_regions.bed')
SAM_FILEPATH = from_here('test_data/sample_mapping.bam')
BC_LIST_FILEPATH = from_here('test_data/sample_bc_table.txt')
