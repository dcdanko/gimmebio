import sys


class Fastx:
    """Represent a sequence record."""

    __slots__ = ('tags', 'sid', 'seq')

    def __init__(self):
        pass

    def parseIdLine(self, rsid):
        sid = rsid.strip()
        if sid[0] in ['>', '@']:
            sid = sid[1:]
        sid = sid.split()
        try:
            self.tags = sid[1:]
        except IndexError as ie:
            self.tags = []
        try:
            self.sid = sid[0]
        except IndexError as ie:
            sys.stderr.write('IDLINE: {}\n'.format(rsid))
            raise ie

    def __len__(self):
        return len(self.seq)


class Fasta(Fastx):
    """Represent a record from a fasta file (no qulaity line)."""

    def __init__(self, sid, seq):
        super(Fasta, self).__init__()
        self.parseIdLine(sid)
        self.seq = seq.strip()

    def __str__(self):
        tags = '\t'.join(self.tags)
        out = '>{} {}\n{}\n'.format(self.sid, tags, self.seq)
        return out

    @classmethod
    def fromRaw(cls, inp):
        if isinstance(inp, str):
            inp = inp.split('\n')
        if len(inp) != 2:
            print(inp)
            assert False
        return Fasta(inp[0], inp[1])


class Fastq(Fastx):
    """Represnt a record from a fastq file."""

    __slots__ = ('delim', 'qual')

    def __init__(self, sid, seq, delim, qual):
        self.parseIdLine(sid)
        self.seq = seq.strip()
        self.delim = delim.strip()
        self.qual = qual.strip()

        assert len(self.qual) == len(self.seq)

    def __str__(self):
        tags = '\t'.join(self.tags)
        out = '@{}\t{}\n{}\n{}\n{}'.format(self.sid,
                                           tags,
                                           self.seq,
                                           self.delim,
                                           self.qual)
        return out

    @classmethod
    def fromRaw(cls, inp):
        if type(inp) == str:
            inp = inp.split('\n')
        assert len(inp) == 4
        return Fastq(inp[0], inp[1], inp[2], inp[3])


class ReadPair:
    """Represent a pair of reads."""

    __slots__ = ('r1', 'r2', 'sid')

    def __init__(self, r1, r2):
        assert r1.sid == r2.sid
        assert isinstance(r1, type(r2))
        self.sid = r1.sid
        self.r1 = r1
        self.r2 = r2

    def __len__(self):
        return len(self.r1) + len(self.r2)

    def __str__(self):
        return str(self.r1) + '\n' + str(self.r2)
