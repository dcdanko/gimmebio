
import gzip
import pandas as pd

from gimmebio.constants import GIMMEBIO_HOME
from os.path import isfile, join
from os import environ


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


def map_taxa_to_contigs(m8file, genfile=None, min_homology=95, min_len=1000):
    """Reurn a nested dictionary mapping the high-homology length of each taxa for each contig."""
    gb_id_tbl, contig_tbl = get_genbank(genfile=genfile), {}
    for tkns in (line.strip().split('\t') for line in m8file):
        contig_id, gbid, perc_id, length = tkns[:4]
        if float(perc_id) < min_homology or int(length) < min_len:
            continue
        ncbi_id = gb_id_tbl.get(gbid, gbid)
        try:
            contig_tbl[contig_id][ncbi_id] += int(length)
        except KeyError:
            contig_tbl[contig_id] = {ncbi_id: int(length)}
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


def assign_contigs(m8file, genfile=None, min_homology=95, min_len=1000, retain_fraction=2):
    """Return a DatFrame with all filtered assignments for all contigs."""
    contig_map = map_taxa_to_contigs(m8file, genfile=genfile, min_homology=min_homology, min_len=min_len)
    assigned = []
    for contig, taxa in contig_map.items():
        assignments = filter_contig_assignments(taxa, retain_fraction=retain_fraction)
        assigned += [
            {'contig': contig, 'taxon': taxon, 'length': length}
            for taxon, length in assignments
        ]
    assigned = pd.DataFrame(assigned)
    return assigned
