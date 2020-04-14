
import subprocess as sp
import gzip
import pandas as pd
from glob import glob
from os.path import join, isfile, basename, abspath

from .plots import coverage_plot, taxa_plot
from .constants import (
    GENOMES,
    FILE_FIELD_DELIM,
    FASTA_EXTENSIONS,
    CONCAT_FASTA,
    BLAST_INDEX,
    KRAKEN2_PATH,
    KRAKEN2_DB_URL,
)


def download_genomes(target_dir, logger=lambda x: None):
    """Download reference genomes for COVID19 pipeline to target dir."""

    def download_one(source_url, target_name):
        cmd = f'wget {source_url} -O {target_name}'
        sp.check_call(cmd, shell=True)

    for (species, strain), url in GENOMES.items():
        target_filename = FILE_FIELD_DELIM.join([species, strain, url.split('/')[-1]])
        target_filename = join(target_dir, target_filename)
        download_one(url, target_filename)


def download_hg38(target_dir, logger=lambda x: None):
    """Download a Bowtie2 index for HG38 with alt contigs."""
    pass


def download_kraken2(target_dir, logger=lambda x: None):
    """Download a custom Kraken2 database for detecting COVID."""
    cmd = (
        f'cd {target_dir} && '
        f'wget {KRAKEN2_DB_URL} && '
        f'tar -xzf {KRAKEN2_DB_URL.split("/")[-1]} '
    )
    sp.check_call(cmd, shell=True)


def make_index(exc, genome_dir, logger=lambda x: None):
    """Make a blastdb named `BLAST_INDEX` from all fastas in genome_dir.

    To make a blastdb it's easiest to concatenate everything into one
    fasta file named `CONCAT_FASTA`
    """
    fastas = []
    for pattern in FASTA_EXTENSIONS:
        fastas += list(glob(f'{genome_dir}/*' + pattern))
    concat_fname = join(genome_dir, CONCAT_FASTA)
    fastas = [fname for fname in fastas if fname != f'{concat_fname}']
    assert not isfile(concat_fname), f'Concat file {concat_fname} already exists. Remove it and rerun.'
    with open(concat_fname, 'a') as concat:
        for fasta in fastas:
            species, strain = basename(fasta).split(FILE_FIELD_DELIM)[:2]
            with gzip.open(fasta) as f:
                for line in (line.decode('utf-8') for line in f):
                    if line[0] == '>':
                        line = f'>{species}{FILE_FIELD_DELIM}{strain}{FILE_FIELD_DELIM}{line[1:]}'
                    concat.write(line)
    cmd = (
        f'{exc} '
        f'-in {join(genome_dir, CONCAT_FASTA)} '
        '-dbtype nucl '
        f'-out {join(genome_dir, BLAST_INDEX)}'
    )
    sp.check_call(cmd, shell=True)


def filter_human_reads(bwt2_exc, genome_dir, reads, outfile, threads=1, logger=lambda x: None):
    """Remove Human reads and write them to `outfile` as a fastq."""
    pass


def kraken2_search_reads(kraken2_exc, genome_dir, reads, outprefix, threads=1, logger=lambda x: None):
    """Use Kraken2 to make a fast pass report on reads. Write report to outfile."""
    reads = abspath(reads)
    cmd = (
        f'{kraken2_exc} '
        f'--db {join(genome_dir, KRAKEN2_PATH)} '
        f'--threads {threads} '
        f'--unclassified-out ${outprefix}.unclassified_num '
        f'--classified-out ${outprefix}.classified_num '
        f'--output ${outprefix}.kraken2_output '
        f'--report ${outprefix}.kraken2_report '
        f'--report-zero-counts '
        f'--gzip-compressed '
        f'{reads}'
    )
    sp.run(cmd, check=True, shell=True)


def search_reads(blast_exc, fq2fa_exc, genome_dir, reads, outfile, threads=1, logger=lambda x: None):
    """Blast reads against the index."""
    reads = abspath(reads)
    cmd = (
        f'gunzip -c {reads} | '
        f'{fq2fa_exc} | '
        f'{blast_exc} '
        f'-db {join(genome_dir, BLAST_INDEX)} '
        '-outfmt 6 '
        '-perc_identity 80 '
        f'-num_threads {threads} '
    )
    sp.run(cmd, check=True, shell=True, stdout=outfile)


def condense_alignment(outfile, aln_file, logger=lambda x: None):
    """Call viruses from the alignment file."""
    pass


def make_report(m8_filename, image_filename, logger=lambda x: None):
    """Make coverage plots for all species detected in the m8 table."""
    tbl = pd.read_csv(
        m8_filename, sep='\t',
        names=[
            'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen',
            'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore'
        ]
    )
    cov = coverage_plot(tbl)
    cov.save(image_filename)


def search_report(blast_exc, fq2fa_exc, genome_dir, reads, m8_filename, image_filename,
                  threads=1, logger=lambda x: None):
    """Search and make a coverage plot."""
    search_reads(
        blast_exc, fq2fa_exc, genome_dir, reads, m8_filename,
        threads=threads, logger=logger
    )
    make_report(m8_filename, image_filename)
