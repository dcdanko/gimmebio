

def baseToInt(base):
    """Return an integer code for the base."""
    base = base.upper()
    if base == 'A':
        return 0
    if base == 'C':
        return 1
    if base == 'G':
        return 2
    if base == 'T':
        return 3
    return 4


def rcBase(base):
    """Return the reverse complement of the base."""
    base = base.upper()
    if base == 'A':
        return 'T'
    if base == 'C':
        return 'G'
    if base == 'G':
        return 'C'
    if base == 'T':
        return 'A'
    return 'N'


def reverseComplement(kmer):
    """Return the reverse complement of the sequence."""
    rc = ''
    for base in kmer[::-1]:
        rc += rcBase(base)
    return rc


def canonical(kmer):
    """Return the canonical representation of a sequence."""
    rc = ''
    for base in kmer[::-1]:
        rc += rcBase(base)
        if kmer < rc:
            return kmer
    return rc
