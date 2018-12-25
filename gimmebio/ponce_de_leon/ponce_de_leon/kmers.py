from .io_utils import open_maybe_gzip, iter_chunks, open_samfile, remove_ext
from subprocess import run, PIPE
from os.path import isfile
from sys import stderr


def reverse_complement(kmer):
    base_map = {'A': 'T', 'G': 'C', 'T': 'A', 'C': 'G', 'N': 'N'}
    rc = ''
    for base in kmer[::-1]:
        rc += base_map[base]
    return rc


def kmer_rotations(kmer):
    rotations = [
        ['N'] * len(kmer)
        for _ in kmer
    ]
    for i, base in enumerate(kmer):
        for j in range(len(kmer)):
            rotations[j][(i + j) % len(kmer)] = base
    return [''.join(rotation) for rotation in rotations]


def rotational_canonicalize(kmer):
    """Return the lexigraphic minimum of rc and rotations of kmer."""
    kmer_class = sorted(
        kmer_rotations(kmer) + kmer_rotations(reverse_complement(kmer))
    )
    return kmer_class[0], kmer_class


def kmerize(seq, k):
    """Produce all kmers in seq."""
    for i in range(len(seq) - k + 1):
        yield seq[i:i + k]


def count_canonical_kmers(fastq_filename, k):
    root_name = remove_ext(fastq_filename, ['fq', 'fastq', 'gz'])
    out_filename = f'{root_name}.{k}-mers.jf'
    if not isfile(out_filename):
        jf_count_cmd = (
            'jellyfish count '
            f'-t {n_threads} -m {k} -s 100M -C '
            f'-o {out_filename} '
            f'{fastq_filename}'
        )
        run(jf_count_cmd, shell=True, check=True)
    return get_rotational_kmer_counts(out_filename)


def count_canonical_kmers_sam(sam_filename, k, n_threads=1):
    root_name = remove_ext(sam_filename, ['sam', 'bam'])
    out_filename = f'{root_name}.{k}-mers.jf'
    if not isfile(out_filename):
        jf_count_cmd = (
            'jellyfish count '
            f'-t {n_threads} -m {k} -s 100M -C '
            f'-o {out_filename} '
            f'<(samtools fasta {sam_filename})'
        )
        run(jf_count_cmd, shell=True, check=True)
    return get_rotational_kmer_counts(out_filename)


def get_rotational_kmer_counts(jf_filename):
    jf_dump_cmd = f'jellyfish dump -c {jf_filename}'
    jf_dump_out = run(jf_dump_cmd, shell=True, check=True, stdout=PIPE, encoding='ISO-8859-1')
    kmer_counts, total_kmers = {}, 0
    for line in jf_dump_out.stdout.split('\n'):
        if len(line) == 0:
            continue
        tkns = line.split()
        kmer, count = tkns[0], int(tkns[1])
        total_kmers += count
        canon_kmer = rotational_canonicalize(kmer)[0]
        kmer_counts[canon_kmer] = count + kmer_counts.get(canon_kmer, 0)

    return kmer_counts, total_kmers
