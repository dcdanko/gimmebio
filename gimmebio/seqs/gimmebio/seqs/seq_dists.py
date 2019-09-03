
import numpy as np


def hamming_distance(seq1, seq2, normalized=True):
    d = 0
    for v1, v2 in zip(seq1, seq2):
        d += 1 if v1 != v2 else 0
    if normalized:
        d /= len(seq1)
    return d


def needle_distance(seq1, seq2, match_score=-1, mismatch_penalty=0.5, gap_penalty=0.6, normalize=True):
    score = np.zeros((len(seq1) + 1, len(seq2) + 1))
    for i in range(len(seq1) + 1):
        score[i][0] = gap_penalty * i
    for j in range(len(seq2) + 1):
        score[0][j] = gap_penalty * j

    def _match_score(b1, b2):
        return match_score if b1 == b2 else mismatch_penalty

    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            match = score[i - 1][j - 1] + _match_score(seq1[i - 1], seq2[j - 1])
            delete = score[i - 1][j] + gap_penalty
            insert = score[i][j - 1] + gap_penalty
            score[i][j] = min(match, delete, insert)
    final_score = score[len(seq1)][len(seq2)]
    if normalize:
        final_score /= min(len(seq1), len(seq2))
    return final_score
