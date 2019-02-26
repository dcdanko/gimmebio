from .color_tree import MasterColorTree


def parse_mpa_to_coltree(mpa_file, colTree=None):
    if colTree is None:
        colTree = MasterColorTree()
    with open(mpa_file) as mf:
        for line in mf:
            tkns = line.strip().split('\t')
            taxa = tkns[0]
            val = float(tkns[1])
            colTree.add_node(taxa, val)
    return colTree
