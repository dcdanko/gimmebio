import cseqs

seq = 'ATCGGTCAGC' # 10 bases

power = 3
radix = 7


def runCatch( func, *args):
    print(func)
    try:
        print(func(*args))
    except Exception as e:
        print(e)

runCatch( cseqs.rabinFingerprints, seq, 10, power, radix)
runCatch( cseqs.makeKmers, seq, len(seq), 3)
runCatch( cseqs.makeCanonicalKmers, seq, len(seq), 3)
runCatch( cseqs.reverseComplement, seq, len(seq))
runCatch( cseqs.canonical, seq, len(seq))
