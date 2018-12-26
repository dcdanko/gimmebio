import networkx as nx
from networkx.algorithms import bipartite
from os.path import isfile
from subprocess import call


def callif(cmd, filename):
    if not isfile(filename):
        call(cmd, shell=True)


def parse_table_file(filename):
    tbl = {}
    with open(filename) as file_handle:
        for line in file_handle:
            tkns = line.split()
            if len(tkns) < 2:
                continue
            tbl[tkns[0]] = tkns[1]
    return tbl


def get_covering_genes(alns):
    G = nx.Graph()
    reads, genes = set(), set()
    with open(alns) as handle:
        for tkns in (line.strip().split('\t') for line in handle):
            if len(tkns) < 2:
                continue
            G.add_edge(tkns[0], tkns[1])
            reads.add(tkns[0])
            genes.add(tkns[1])
    covered_reads, covering_genes = set(), set()
    genes = sorted([(gene, degree) for gene, degree in G.degree(genes)], key=lambda x: -x[1])
    for gene, _ in genes:
        my_reads = set(G.neighbors(gene))
        if len(my_reads) < 3 or len(my_reads & covered_reads) == len(my_reads):
            continue
        covering_genes.add(gene)
        covered_reads.update()
        if len(covered_reads) == len(reads):
            break
    return covering_genes


def parse_bx_to_gene(bx_to_gene):
    with open(bx_to_gene) as bx_to_gene_handle:
        bx_to_gene_handle.readline()
        tbl = {}
        for line in bx_to_gene_handle:
            tkns = line.strip().split('\t')
            if len(tkns) < 3:
                continue
            bx, gene, weight = tkns[:3]
            try:
                tbl[gene].append((bx, weight))
            except KeyError:
                tbl[gene] = [(bx, weight)]
    return tbl


def gene_dist(gset0, gset1):
    gset0, gset1 = {bx for bx, _ in gset0}, {bx for bx, _ in gset1}
    jaccard = len(gset0 & gset1) / len(gset0 | gset1)
    return 1 - jaccard


def build_weighted_graph(edge_handle):
    G = nx.Graph()
    for line in edge_handle:
        tkns = line.strip().split('\t')
        if len(tkns) < 3:
            continue
        if 0 < float(tkns[2]) < 1:
            G.add_edge(tkns[0], tkns[1])
    return G
