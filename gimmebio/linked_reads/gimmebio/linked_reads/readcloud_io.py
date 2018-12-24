"""Parse ReadCloud files."""

from gimmebio.seqs.fastx_io import iterFastq

from .exceptions import NoGemcodeException, GemcodeMismatchException
from .readclouds import ReadCloud, ChromiumReadPair


def iterReadCloud(filelike):
    rC = ReadCloud(None)
    for rP in iterFastq(filelike, interleaved=True):
        try:
            cRP = ChromiumReadPair.fromReadPair(rP)
        except NoGemcodeException:
            continue

        try:
            rC.addPair(cRP)
        except GemcodeMismatchException:
            yield rC
            rC = ReadCloud(cRP.barcode)
            rC.addPair(cRP)
    yield rC
