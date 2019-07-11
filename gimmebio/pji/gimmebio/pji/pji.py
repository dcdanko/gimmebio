
from .utils import get_mad


def top_taxa(df, major_ratio=2):
    maxk = max(df['kmers'])
    if maxk > 512:
        df = df[df['kmers'] >= 512]
    else:
        return None
    df['percent'] = 100 * (df['percent'] / sum(df['percent']))
    df = df[df['percent'] >= 0]
    major_taxa = True
    if df.shape[0] >= 2:
        second_max, first_max = sorted(df['percent'])[-2:]
        major_taxa = (first_max / second_max) >= major_ratio
    if major_taxa:
        df['is_major'] = df['percent'] == max(df['percent'])
        df = df[df['percent'] >= 5]
    else:
        df['is_major'] = False
    return df


def median_filter(df, contaminants):
    """Remove contaminants unless they are an outlier."""
    devs = {}
    for contam in contaminants:
        contam_df = df[df['taxa_name'] == contam]
        dup_med, dup_mad = get_mad(contam_df['dup'])
        kmer_med, kmer_mad = get_mad(contam_df['kmers'])
        devs[contam] = (dup_med - (2 * dup_mad), kmer_med + (2 * kmer_mad))
    rows = []
    for _, row in df.iterrows():
        if row['taxa_name'] not in contaminants:
            rows.append(True)
            continue
        dup_thresh, kmer_thresh = devs[row['taxa_name']]
        if (row['dup'] < dup_thresh) and (row['kmers'] > kmer_thresh):
            rows.append(True)
            continue
        rows.append(False)
    return df[rows]


def find_contam(df, contaminant_prevalence=0.5, use_mad_filter=False):
    """Flag taxa that occur in too many samples."""
    taxa_counts = {}
    for taxa in df['taxa_name']:
        taxa_counts[taxa] = 1 + taxa_counts.get(taxa, 0)

    thresh = max(2, contaminant_prevalence * len(set(df['sample_name'])))
    contaminants = {taxa for taxa, count in taxa_counts.items() if count >= thresh}

    if not use_mad_filter or df.shape[0] <= 2:
        return df[~df['taxa_name'].isin(contaminants)]
    return median_filter(df, contaminants)


def identify_pji_taxa(longform_taxa_table, contam_thresh=0.5):
    contam_removed = find_contam(longform_taxa_table, contaminant_prevalence=contam_thresh)
    reprocessed_taxa = contam_removed.groupby(by='sample_name', group_keys=False).apply(top_taxa)
    return reprocessed_taxa

