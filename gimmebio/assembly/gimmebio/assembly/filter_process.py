
import networkx as nx
import pandas as pd
import pysam
from Bio import SeqIO



def filter_homologous(m8file, fasta, min_perc_id=0.95, min_len_frac=0.8):
    """Return a generator of contigs.

    Filter contigs that are homologous to one another keeping the largest.

    Find connected components in the m8 file (presumed to be an
    autologous alignment). Edges exist between contigs where
    an alignment is:
    1) Greater than <min_perc_id> similar
    2) Longer than <min_len_frac> * min(len(c1), len(c2))
    For each component take the longest contig and write it to a fasta.
    """
    length_map = {rec.id: len(rec.seq) for rec in SeqIO.parse(fasta, 'fasta')}
    fasta.seek(0)
    components = find_m8_components(
        m8file, length_map, min_perc_id=min_perc_id, min_len_frac=min_len_frac
    )
    my_maxes = set()
    for component in components:
        max_contig = None
        for contig in component:
            if max_contig is None or length_map[contig] > length_map[max_contig]:
                max_contig = contig
        my_maxes.add(max_contig)

    for rec in SeqIO.parse(fasta, 'fasta'):
        if rec.id in my_maxes:
            yield rec


def find_m8_components(m8file, length_map, min_perc_id=0.95, min_len_frac=0.8):
    """Return an iterator of sets where each set lists contigs in a component."""
    G = nx.Graph()
    for tkns in (line.strip().split('\t') for line in m8file):
        c1, c2, perc_id, length = tkns[:4]
        length, perc_id = int(length), float(perc_id)
        if perc_id < min_perc_id:
            continue
        if length < (min_len_frac * min(length_map[c1], length_map[c2])):
            continue
        G.add_edge(c1, c2)
    return nx.algorithms.components.connected_components(G)


def rpkm_from_one_bam(bamfile, contig_lengths, groups={}):
    """Return a pandas series with rpkm values for each contig in the bam.

    Optionally group contigs together treating them as a single large contig.
    """
    sam = pysam.Samfile(bamfile, "rb")
    reads_per_group = {}
    for aln in sam:
        if aln.is_unmapped:
            continue
        if aln.is_secondary or aln.is_duplicate or aln.is_supplementary:
            continue
        if aln.is_read2:  # debatable
            continue
        group_name = groups.get(aln.reference_name, aln.reference_name)
        reads_per_group[group_name] = 1 + reads_per_group.get(group_name, 0)

    group_reverse = {}
    for contig, group in groups.items():
        mygroup = group_reverse.get(group, set())
        mygroup.add(contig)
        group_reverse[group] = mygroup

    million_reads = float(pysam.view("-c", bamfile)[0].strip("\n")) / (1000 * 1000)
    rpkm = {}
    for group, nreads in reads_per_group.items():
        try:
            kbp = contig_lengths[group]  # if the contig was not in a group
        except KeyError:
            kbp = sum([contig_lengths[contig] for contig in group_reverse[group]])
        rpkm[group] = nreads / (kbp * million_reads)
    return pd.Series(rpkm)


def rpkm_from_bams(bamfiles, fasta, groups={}):
    """Return a pandas dataframe with RPKM values for each contig."""
    length_map = {rec.id: len(rec.seq) for rec in SeqIO.parse(fasta, 'fasta')}
    rpkms = pd.DataFrame.from_dict({
        sample_name: rpkm_from_one_bam(bamfile, length_map, groups=groups)
        for sample_name, bamfile in bamfiles.items()
    }, orient='index').fillna(0)
    return rpkms

