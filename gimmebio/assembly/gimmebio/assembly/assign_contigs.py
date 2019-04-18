
import gzip
import pandas as pd

from gimmebio.constants import GIMMEBIO_HOME
from Bio import SeqIO
from os.path import isfile, join
from os import environ


def get_ncbi_id(gbid, gb_id_tbl):
    gbid = gbid.split('.')[0]
    try:
        return gb_id_tbl[gbid]
    except KeyError:
        ncbi_id = None
        for sub_id in gbid.split('|'):
            sub_id = sub_id.split('.')[0]
            ncbi_id = gb_id_tbl.get(sub_id, None)
    return ncbi_id


def get_genbank(genfile=None):
    """Return a dictionary mapping genbank ids to species names."""
    if not isfile(genfile):
        try:
            genfile = environ['GIMMEBIO_GENBANK_IDS']
        except KeyError:
            genfile = join(GIMMEBIO_HOME, 'genbank_taxa_ids_to_binomial_species_names.tsv.gz')
            if not isfile(genfile):
                url = 'https://s3.wasabisys.com/metasub/genbank_taxa_ids_to_binomial_species_names.tsv.gz'
                # TODO: Download file if missing
    id_tbl = {}
    with gzip.open(genfile) as gf:
        for tkns in (line.decode('utf-8').strip().split('\t') for line in gf):
            id_tbl[tkns[0]] = tkns[1]
    return id_tbl


def map_taxa_to_contigs(m8file, min_homology=95, min_len=1000):
    """Reurn a nested dictionary mapping the high-homology length of each taxa for each contig."""
    contig_tbl = {}
    for tkns in (line.strip().split('\t') for line in m8file):
        contig_id, gbid, perc_id, length = tkns[:4]
        length, perc_id = int(length), float(perc_id)
        if perc_id < min_homology or length < min_len:
            continue
        my_contig_tbl = contig_tbl.get(contig_id, {})
        my_contig_tbl[gbid] = length + my_contig_tbl.get(gbid, 0)
        contig_tbl[contig_id] = my_contig_tbl
    return contig_tbl


def filter_contig_assignments(taxa, retain_fraction=2):
    """Return a filtered list of taxa assignments for a contig sorted with the best first."""
    max_len = max(taxa.values())
    min_thresh = max_len // retain_fraction
    filtered = sorted([
        (taxon, homologous_len)
        for taxon, homologous_len in taxa.items()
        if homologous_len >= min_thresh
    ], key=lambda x: -x[1])
    return filtered


def assign_contigs(m8file, genfile=None, seqfile=None, min_homology=95, min_len=1000, retain_fraction=2):
    """Return a DatFrame with all filtered assignments for all contigs."""
    gb_id_tbl = get_genbank(genfile=genfile)
    contig_map = map_taxa_to_contigs(m8file, min_homology=min_homology, min_len=min_len)
    assigned = []
    for contig, taxa in contig_map.items():
        assignments = filter_contig_assignments(taxa, retain_fraction=retain_fraction)
        assigned += [
            {
                'contig': contig,
                'original_id': gbid,
                'taxon': get_ncbi_id(gbid, gb_id_tbl),
                'length': length,
            }
            for gbid, length in assignments
        ]
    assigned = pd.DataFrame(assigned)
    if seqfile:
        seqlens = pd.Series({
            rec.name: len(rec.seq)
            for rec in SeqIO.parse(seqfile, 'fasta')
        })
        contig_lengths = list(seqlens[assigned['contig']])
        assigned['contig_length'] = contig_lengths
        assigned['contig_length_fraction'] = list(assigned['length'] / contig_lengths)

    return assigned
