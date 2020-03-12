
import subprocess as sp
from glob import glob
from os.path import join

from .constants import (
    GENOMES,
    FILE_FIELD_DELIM,
    FASTA_EXTENSIONS,
    CONCAT_FASTA,
    BLAST_INDEX,
)


def download_genomes(target_dir, logger=lambda x: None):
    """Download reference genomes for COVID19 pipeline to target dir."""

    def download_one(source_url, target_name):
        cmd = f'wget {source_url} -O {target_name}'
        sp.check_call(cmd, shell=True)

    for (species, strain), url in GENOMES.items():
        target_filename = FILE_FIELD_DELIM.join([species, strain, url.split('/')[-1]])
        target_filename = join(target_dir, target_filename)
        download_one(url. target_filename)


def make_index(exc, genome_dir, logger=lambda x: None):
    """Make a blastdb named `BLAST_INDEX` from all fastas in genome_dir.

    To make a blastdb it's easiest to concatenate everything into one
    fasta file named `CONCAT_FASTA`
    """
    fastas = []
    for pattern in FASTA_EXTENSIONS:
        fastas += list(glob(f'{genome_dir}/*' + pattern))
    fastas = [fname for fname in fastas if fname != CONCAT_FASTA]
    cmd = f'gunzip -c {' '.join(fastas)} > {CONCAT_FASTA}'
    sp.check_call(cmd, shell=True)
    cmd = (
        f'{exc} '
        f'-in {CONCAT_FASTA} '
        '-dbtype nucl '
        f'-title {BLAST_INDEX}'
    )
    sp.check_call(cmd, shell=True)


def search_reads(blast_exc, fq2fa_exc, genome_dir, reads, outfilename, threads=1, logger=lambda x: None):
    """Blast reads against the index."""
    cmd = (
        f'{blast_exc} '
        f'-db {genome_dir}/{BLAST_INDEX}'
        '-outfmt 6 '
        '-perc_identity 80 '
        f'-num_threads {threads} '
        f'-query <(gunzip -c {reads} | {fq2fa_exc}) '
        f'> {outfilename}'
    )
    sp.check_call(cmd, shell=True)


def condense_alignment(outfile, aln_file, logger=lambda x: None):
    """Call viruses from the alignment file."""
    pass
