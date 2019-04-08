from math import log
from subprocess import check_output


def counts_from_jf(jf_filename):
    """Yield kmer counts from a jellyfish file."""
    out = check_output(f'jellyfish dump -c {jf_filename}', shell=True, universal_newlines=True)
    for line in out.splitlines():
        if not line.strip():
            continue
        tkns = line.strip().split()
        yield int(tkns[1])



def jf_stats(jf_filename):
    raw_counts = []
    stats = {
        'n_kmers': 0,
        'n_singletons': 0,
        'max_count': 0,
        'total_kmers': 0,
    }
    for count in counts_from_jf(jf_filename):
        stats['n_kmers'] += 1
        stats['total_kmers'] += count
        if count == 1:
            stats['n_singletons'] += 1
        if count > stats['max_count']:
            stats['max_count'] = count
        raw_counts.append(count)

    entropy, mean = 0, 0
    for count in raw_counts:
        p = count / stats['total_kmers']
        entropy += p * log(p, 2)
        mean += count
    mean /= len(raw_counts)
    entropy *= -1
    stats['entropy'] = entropy
    stats['mean'] = mean
    return stats
