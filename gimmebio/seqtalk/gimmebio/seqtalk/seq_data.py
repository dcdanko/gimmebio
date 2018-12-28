
import numpy as np
from random import random
from Bio import SeqIO

MILLION = 1000 * 1000


def seq_to_matrix(seq):
    """Return a four color indicator encoding of a sequence as a row 'vector'."""
    seq = seq.upper()
    return np.matrix([
        [1 if seqb == base else 0 for seqb in seq] for base in 'ACGT'
    ])


class ShortReadData:

    def __init__(self, seq_len, seqs=[]):
        self.index = 0
        self.seqs, self.seq_len = seqs, seq_len

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, i):
        return self.seqs[i % len(self)]

    def reset(self):
        self.index = 0

    def process_seq(self, seq):
        diff = len(seq) - self.seq_len
        diff //= 2
        return seq_to_matrix(seq[diff:(diff + self.seq_len)])

    def next_batch(self, batch_size):
        batch = [
            self.process_seq(self[self.index + i])
            for i in range(batch_size)
        ]
        self.index += batch_size
        return batch


class FastqSeqData:

    def __init__(self, filename, seq_len=100, split_frac=0.8, total=10 * MILLION):
        self.train, self.test = ShortReadData(seq_len), ShortReadData(seq_len)
        with open(filename) as fastq_handle:
            for i, rec in enumerate(SeqIO.parse(fastq_handle, "fastq")):
                if i >= total:
                    break
                if random() < split_frac:
                    self.train.seqs.append(rec.seq)
                else:
                    self.test.seqs.append(rec.seq)
