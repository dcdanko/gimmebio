
from subprocess import call
from os.path import isfile

from .utils import *


def filter_human_reads(sample_name, reads, human_genome):
    unaligned_reads = f'{sample_name}.not_human.fq'
    cmd = (
        'bowtie2 '
        f'-x {human_genome} '
        f'-U {reads} '
        f'--un {unaligned_reads} '
        '> /dev/null'
    )
    callif(cmd, unaligned_reads)
    return unaligned_reads


def align_to_genes(sample_name, reads, gene_db):
    aln_file = f'{sample_name}.diamond_uniref90.m8.gz'
    cmd = (
        'diamond blastx '
        '--tmpdir . '
        '--threads 8 '
        f'-d {gene_db} '
        f'-q {reads} '
        f'| gzip > {aln_file}'
    )
    callif(cmd, aln_file)
    return aln_file


def filter_bad_align(sample_name, alns):
    filt_alns = f'filt.diamond_uniref90.m8'
    cmd = f'zcat {alns} | awk \"{{if(\$3 >= 80) print \$0}}\" > {filt_alns}'
    callif(cmd, filt_alns)
    return filt_alns


def read_to_gene_map(sample_name, alns):

    def get_best(block):
        return '\t'.join(sorted(block, key=lambda x: float(x[10]))[0])

    out_filename = f'best.{alns}'
    if isfile(out_filename):
        return out_filename
    covering_genes = get_covering_genes(alns)
    with open(alns) as handle, open(out_filename, 'w') as out_file:
        cur_id, cur_block = '', []
        for line in handle:
            tkns = line.strip().split('\t')
            if tkns[0] == cur_id:
                if tkns[1] in covering_genes:
                    cur_block.append(tkns)
            else:
                if len(cur_block):
                    out_file.write(get_best(cur_block) + '\n')
                    cur_id, cur_block = '', []
                if tkns[1] in covering_genes:
                    cur_id, cur_block = tkns[0], [tkns]
        if cur_block:
            out_file.write(get_best(cur_block) + '\n')
    return out_filename


def get_rid_to_bx(sample_name, reads):
    map_file = f'{sample_name}.rids_to_bx.tsv'
    cmd = (
        f'cat {reads} | grep -F \'BX\' | '
        'tr \'@\' \' \' | awk \'{print $1 "\t" $2}\' > '
        f'{map_file}'
    )
    callif(cmd, map_file)
    return map_file


def get_bx_to_gene(sample_name, rid_to_bx, alns):
    map_file = f'{sample_name}.bx_to_gene.tsv'
    if isfile(map_file):
        return map_file
    rid_to_bx, rid_to_gene = parse_table_file(rid_to_bx), parse_table_file(alns)
    tbl = {}
    for rid, gene in rid_to_gene.items():
        try:
            bx = rid_to_bx[rid]
            tbl[(bx, gene)] = 1 + tbl.get((bx, gene), 0)
        except KeyError:
            pass

    with open(map_file, 'w') as handle:
        for (bx, gene), count in tbl.items():
            if count >= 2:
                handle.write(f'{bx}\t{gene}\t{count}\n')

    return map_file


def get_gene_distance(sample_name, bx_to_gene):
    dist_matrix = f'{sample_name}.gene_gene_dist.tsv'
    with open(dist_matrix, 'w') as out_file:
        bx_to_gene = parse_bx_to_gene(bx_to_gene)
        for gene0, gset0 in bx_to_gene.items():
            for gene1, gset1 in bx_to_gene.items():
                d = gene_dist(gset0, gset1)
                out_file.write(f'{gene0}\t{gene1}\t{d}\n')
    return dist_matrix


def find_components(sample_name, gene_dist):
    component_file = f'{sample_name}.connected_components.txt'
    with open(gene_dist) as edge_file, open(component_file, 'w') as compfile:
        G = build_weighted_graph(edge_file)
        for comp in nx.connected_components(G):
            if len(comp) == 1:
                continue
            print(' '.join(comp), file=compfile)
