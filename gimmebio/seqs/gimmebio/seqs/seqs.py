

def baseToInt(base):
    """Return an integer code for the base."""
    if base == 'A':
        return 0
    elif base == 'C':
        return 1
    elif base == 'G':
        return 2
    elif base == 'T':
        return 3
    else:
        return 4


def rcBase(base):
    """Return the reverse complement of the base."""
    if base == 'A':
        return 'T'
    elif base == 'C':
        return 'G'
    elif base == 'G':
        return 'C'
    elif base == 'T':
        return 'A'
    else:
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
