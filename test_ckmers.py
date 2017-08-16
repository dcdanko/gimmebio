import ckmers
import gimmebio.kmers as kmers

seq = 'ATCGGTCAGC' # 10 bases

power = 3
radix = 7

fps = kmers.rabinFingerprints(seq, 1 + 2**power, prime=radix)
print(fps)
print(ckmers.nextRabinFingerprint(fps[0][1], 0, 1, power, radix))
print(ckmers.rabinFingerprints(seq, 10, power, radix))
