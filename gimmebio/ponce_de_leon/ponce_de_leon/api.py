from .io_utils import *
from .kmers import (
    count_canonical_kmers,
    count_canonical_kmers_sam,
    rotational_canonicalize,
    get_rotational_kmer_counts,
)
from sys import stdout
from pysam import AlignmentFile as SamFile


def read_in_regions(read, regions):
    try:
        coords = regions[read.reference_name]
        pos = read.reference_start
        for (start, end) in coords:
            return (start <= pos) and (end >= pos)
    except KeyError:
        return False

    
def get_bcs_in_region(sam_file, bed_file, fastq_file=None):
    bcs = set()
    regions = parse_bed_file(bed_file)
    sam_file = open_samfile(sam_file)
    if fastq_file is not None:
        bc_map = parse_bc_map(fastq_file)
    
    for read in sam_file:
        if read_in_regions(read, regions):
            if fastq_file is None:
                try:
                    bcs.add(get_bc_sam(read))
                except KeyError:
                    pass
            else:
                bcs.add(bc_map[read.query_name])
            
    sam_file.close()
    return bcs


def get_reads_with_bcs_fastq(bc_file, fastq_file):
    bcs = parse_bc_list(bc_file)
    fastq_file = open_maybe_gzip(fastq_file)
    for chunk in iter_chunks(fastq_file, 4):
        id_line = chunk[0]
        bc = get_bc_token(id_line)
        if bc in bcs:
            yield chunk
    fastq_file.close()


def get_reads_with_bcs_sam(bc_file, sam_file, out_handle=stdout):
    bcs = parse_bc_list(bc_file)
    sam_file = open_samfile(sam_file)
    sam_out = SamFile(out_handle, "w", template=sam_file)
    for read in sam_file:
        try:
            bc = get_bc_sam(read)
            if bc in bcs:
                continue
            sam_out.write(read)
        except KeyError:
            pass
    sam_file.close()
    sam_out.close()


def count_kmer_classes(fastq_file, k=6, sam=False, rotations=False):
    if rotations:
        kmer_counts, total_kmers = get_rotational_kmer_counts(fastq_file)
    elif sam:
        kmer_counts, total_kmers = count_canonical_kmers_sam(fastq_file, k)        
    else:
        kmer_counts, total_kmers = count_canonical_kmers(fastq_file, k)
    return {
        kmer: {
            'total': count,
            'frequency': count / total_kmers,
            'k': k,
            'sequences': ' '.join(rotational_canonicalize(kmer)[1]),
        } for kmer, count in kmer_counts.items()
    }
