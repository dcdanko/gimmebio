

from .fastx import (
    Fasta,
    Fastq,
    ReadPair,
)


def iterChunks(filelike, n):
    chunk = []
    for line in filelike:
        chunk.append(line)
        if len(chunk) == n:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def iterFastq(filelike, interleaved=False):
    n = 4
    if interleaved:
        n = 8
    for chunk in iterChunks(filelike, n):
        r1 = Fastq.fromRaw(chunk[:4])
        if interleaved:
            r2 = Fastq.fromRaw(chunk[4:])
            yield ReadPair(r1, r2)
        else:
            yield r1


def iterFasta(filelike):
    curChunk = [None, '']
    for line in filelike:
        line = line.strip()
        if line[0] == '>':
            if curChunk[0] is not None:
                yield Fasta.fromRaw(curChunk)
                curChunk = [None, '']
            curChunk[0] = line
        else:
            curChunk[1] += line
    yield Fasta.fromRaw(curChunk)
