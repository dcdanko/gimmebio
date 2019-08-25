import numpy as np
from gimmebio.ram_seq import rs_matrix, seq_power_series
from scipy.spatial import KDTree

HAMMING_CONVERSION = {
    0: 0.0,
    1: 0.11799644906568713,
    2: 0.16481916364930368,
    3: 0.18738563790681223,
    4: 0.23185175677791192,
    5: 0.2436776512999408,
    6: 0.2940596155706582,
    7: 0.3020945579811154,
    8: 0.3079275949867765,
    9: 0.3380424375364427,
    10: 0.35320303951951315,
    11: 0.3380300621493104,
    12: 0.349599942648985,
    13: 0.3780828659466007,
    14: 0.3286042507039876,
    15: 0.3233414465917246,
    16: 0.35605066696664267,
    17: 0.33124235423128423,
    18: 0.3528181820051307,
    19: 0.35772577870122213,
    20: 0.38077087198565873,
    21: 0.37561436941880827,
    22: 0.3810799085511973,
    23: 0.3784886103597169,
}

SEED_SIZE = 10 * 1000
BALANCE_GAP = 10 * 1000
BATCH_SIZE = 1000


class KDRFTCover:

    def __init__(self, hamming_radius):
        self.rf_coeffs = None
        self.points = []
        self.centroids = []
        self.batch = []
        self.radius = HAMMING_CONVERSION[hamming_radius]
        self.closed = False
        self.clusters = {}
        self.tree = None

    def ramify(self, kmer):
        if self.rf_coeffs is None:
            self.rf_coeffs = rs_matrix(len(kmer))
        rft = seq_power_series(kmer, RS=self.rf_coeffs)[:min(16, len(kmer))]
        return np.array(rft)

    def add(self, kmer):
        self.closed = False
        rft = self.ramify(kmer)
        if self.tree is None:
            self.points.append(rft)
            self.centroids.append(rft)
            index = len(self.centroids) - 1
            self.clusters[index] = set([index])
            if len(self.centroids) == SEED_SIZE:
                print('Building seed tree...')
                self.build()

        else:
            self.batch.append(rft)
            if len(self.batch) % BATCH_SIZE == 0:
                self.batch_add()

    def batch_add(self):
        if not self.batch:
            return
        print('Adding batch...')
        dists, points = self.tree.query(
            np.array(self.batch), eps=0.2, distance_upper_bound=self.radius
        )
        for i, (dist, centroid) in enumerate(zip(dists, points)):
            rft = self.batch[i]
            if dist > self.radius:  # the closest centroid is not close enough
                self.centroids.append(rft)
                index = len(self.centroids) - 1
                self.clusters[index] = set([index])
            else:
                self.clusters[centroid].add(len(self.points) + i)
        self.points += self.batch
        self.batch = []

        print('Rebuilding tree...')
        self.build()

    def build(self):
        if self.tree is not None:
            self.batch_add()
        self.tree = KDTree(np.array(self.centroids))

    def close(self):
        if not self.closed:
            self.build()
            self.closed = True

    def search(self, kmer, max_dist):
        self.close()
        rft = self.ramify(kmer)
        centroids = self.tree.query_ball_point(rft, HAMMING_CONVERSION[max_dist], eps=0.01)
        return centroids

    def greedy_clusters(self):
        self.close()
        clusters, clustered_points = {}, set()
        if not self.closed:
            self.build()
        for i, rft in enumerate(self.points):
            if i in clustered_points:
                continue
            clusters[i] = set([i])
            clustered_points.add(i)
            pts = set(self.tree.query_ball_point(rft, self.radius, eps=0.01))
            pts -= clustered_points
            clusters[i] |= pts
            clustered_points |= pts
        self.clusters = clusters

    def stats(self):
        #self.greedy_clusters()
        return {
            'num_kmers': sum([len(clust) for clust in self.clusters.values()]),
            'num_singletons': sum([
                1 if len(clust) == 1 else 0 for clust in self.clusters.values()
            ]),
            'num_clusters': len(self.clusters),
        }
