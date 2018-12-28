"""Represent readclouds."""

from gimmebio.seqs.fastx import ReadPair

from .exceptions import NoGemcodeException, GemcodeMismatchException


class ChromiumReadPair(ReadPair):
    """Represent a pair of barcoded reads."""

    __slots__ = ('barcode',)

    def __init__(self, r1, r2):
        super(ChromiumReadPair, self).__init__(r1, r2)
        self.barcode = None
        for tag in r1.tags:
            if 'BX:' in tag:
                self.barcode = tag
                break
        if self.barcode is None:
            raise NoGemcodeException()
        for tag in r2.tags:
            if 'BX:' in tag:
                if tag != self.barcode:
                    raise GemcodeMismatchException()

    @classmethod
    def fromReadPair(cls, readPair):
        return ChromiumReadPair(readPair.r1, readPair.r2)


class ReadCloud:
    """Represent a read cloud."""

    __slots__ = ('barcode', 'readPairs')

    def __init__(self, barcode, readPairs=[]):
        self.barcode = barcode
        self.readPairs = []

        for rP in readPairs:
            self.addPair(rP)

    def addPair(self, cRP):
        if not isinstance(cRP, ChromiumReadPair):
            raise TypeError()
        if self.barcode is not None:
            if self.barcode != cRP.barcode:
                raise GemcodeMismatchException()
        else:
            self.barcode = cRP.barcode
        self.readPairs.append(cRP)

    def getSeqs(self):
        out = []
        for rP in self.readPairs:
            out.append(rP.r1.seq)
            out.append(rP.r2.seq)
        return out

    def __iter__(self):
        return iter(self.readPairs)

    def __str__(self):
        out = ''
        for rp in self.readPairs:
            out += str(rp) + '\n'
        return out

    def __len__(self):
        return len(self.readPairs)
