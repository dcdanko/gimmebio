import numpy as np
import pandas as pd
from gimmebio.ram_seq import rs_matrix, seq_power_series
from scipy.spatial import KDTree

HAMMING_CONVERSION = {
    0: 0.0,
    1: 0.05,
    2: 0.10,
    3: 0.15,
    4: 0.20,
}

SEED_SIZE = 10 * 1000
BALANCE_GAP = 10 * 1000
BATCH_SIZE = 1000


def hamming_distance(k1, k2):
    d = 0
    for v1, v2 in zip(k1, k2):
        d += 1 if v1 != v2 else 0
    return d


class KDRFTCover:

    def __init__(self, hamming_radius, seed_size=-1):
        self.rf_coeffs = None
        self.seed_size = seed_size
        self.points = []
        self.centroids = []
        self.batch = []
        self.radius = HAMMING_CONVERSION[hamming_radius]
        self.clusters = {}
        self.tree = None
        self.raw = []

    def ramify(self, kmer):
        if self.rf_coeffs is None:
            self.rf_coeffs = rs_matrix(len(kmer))
        rft = seq_power_series(kmer, RS=self.rf_coeffs)[:min(16, len(kmer))]
        return np.array(rft)

    def add(self, kmer):
        self.raw.append(kmer)
        rft = self.ramify(kmer)
        self.points.append(rft)

    def search(self, kmer, max_dist):
        rft = self.ramify(kmer)
        centroids = self.tree.query_ball_point(rft, HAMMING_CONVERSION[max_dist], eps=0.01)
        return centroids

    def greedy_clusters(self):
        self.tree = KDTree(np.array(self.points))
        clusters, clustered_points = {}, set()
        for i, rft in enumerate(self.points):
            if i in clustered_points:
                continue
            clusters[i] = set([i])
            clustered_points.add(i)
            pts = set(self.tree.query_ball_point(rft, self.radius, eps=0.1))
            pts -= clustered_points
            clusters[i] |= pts
            clustered_points |= pts
        self.clusters = clusters
        self.centroids = [self.points[i] for i in clusters.keys()]
        self.tree = KDTree(np.array(self.centroids))

    def _cluster_radius(self):
        all_dists = []
        for centroid, cluster in self.clusters.items():
            centroid, dists = self.raw[centroid], []
            for point in [self.raw[i] for i in cluster]:
                dists.append(hamming_distance(centroid, point))
            all_dists.append(pd.Series(dists).quantile([0.5, 0.80, 0.95, 1]))
        all_quants = pd.DataFrame(all_dists).mean()
        return all_quants

    def stats(self):
        r50, r80, r95, r100 = self._cluster_radius()
        return {
            'num_kmers': sum([len(clust) for clust in self.clusters.values()]),
            'num_singletons': sum([
                1 if len(clust) == 1 else 0 for clust in self.clusters.values()
            ]),
            'num_clusters': len(self.clusters),
            'radius_50': r50,
            'radius_80': r80,
            'radius_95': r95,
            'radius_100': r100,
        }
