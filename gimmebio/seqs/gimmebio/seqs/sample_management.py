
from os.path import basename


def get_sample_name_and_end(filename):
    """Return a tuple of sample name and read end."""
    base = basename(filename)
    for pattern, end in [('_R1.', 1), ('.R1.', 1), ('_1.', 1), ('_R2.', 2), ('.R2.', 2), ('_2.', 2)]:
        if pattern in base:
            return base.split(pattern)[0], end
    for pattern in ['.fq', '.fastq', '.fna', '.faa', '.fasta']:
        if pattern in base:
            return base.split(pattern)[0], 0
    assert False  # pattern unknown
