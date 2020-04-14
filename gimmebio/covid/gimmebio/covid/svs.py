
import pandas as pd


def process_one_split_read(aln):
    chimera_tag = aln.get_tag('SA')
    split_pos = int(chimera_tag.split(',')[1])
    return {
        'read_name': aln.query_name,
        'position': aln.reference_start,
        'mate_position': aln.next_reference_start,
        'is_primary_alignment': not aln.is_supplementary,
        'split_position': split_pos,
        'min_pos': min(aln.reference_start, split_pos),
        'max_pos': max(aln.reference_start, split_pos),
    }


def tabulate_split_read_signatures(aln_file, min_gap=100, primary_only=False):
    """Return a pandas dataframe with the following fields
    - read name
    - leftmost position of the read on the reference
    - position of the mate pair on the reference
    - mapping quality
    - primary alignment flag.

    restrict this only to reads with the `SA` tag
    """
    tbl = []
    for aln in aln_file:
        try:
            aln.get_tag('SA')
            tbl.append(process_one_split_read(aln))
        except KeyError:
            pass
    tbl = pd.DataFrame(tbl)
    if primary_only:
        tbl = tbl.loc[tbl['is_primary_alignment']]
    tbl = tbl.loc[(tbl['position'] - tbl['split_position']).abs() >= min_gap]
    return tbl
