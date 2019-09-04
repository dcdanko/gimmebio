import numpy as np
import pandas as pd
from gimmebio.ram_seq import rs_matrix, seq_power_series
from gimmebio.seqs import (
    hamming_distance,
    needle_distance,
)
from scipy.spatial import KDTree


SEED_SIZE = 10 * 1000
BALANCE_GAP = 10 * 1000
BATCH_SIZE = 1000


class KDRFTCover:

    def __init__(self, radius, seed_size=-1):
        self.rf_coeffs = None
        self.seed_size = seed_size
        self.points = []
        self.centroids = []
        self.batch = []
        self.radius = radius
        self.clusters = {}
        self.tree = None
        self.raw = []

    def ramify(self, kmer):
        if self.rf_coeffs is None:
            self.rf_coeffs = rs_matrix(len(kmer))
        rft = seq_power_series(kmer, RS=self.rf_coeffs)[:min(12, len(kmer))]
        return np.array(rft)

    def add(self, kmer):
        self.raw.append(kmer)
        rft = self.ramify(kmer)
        self.points.append(rft)

    def search(self, kmer, max_dist):
        rft = self.ramify(kmer)
        centroids = self.tree.query_ball_point(rft, max_dist, eps=0.01)
        return centroids

    def greedy_clusters(self, logger=None):
        all_tree, index_map = KDTree(np.array(self.points)), {i: i for i in range(len(self.points))}
        clusters, clustered_points = {}, set()
        batch_map, batch_points = {}, []
        for i, rft in enumerate(self.points):
            if i in clustered_points:
                continue
            batch_map[len(batch_points)] = i
            batch_points.append(rft)
            if len(batch_points) == 1000:
                if logger is not None:
                    logger(f'Running batch, starting with {len(clusters)} clusters')
                clusters, clustered_points = self._greedy_cluster_batch(
                    all_tree, index_map,
                    batch_map, batch_points,
                    clusters, clustered_points
                )
                batch_map, batch_points = {}, []

                # Rebuild all_tree to only include points which are not yet clustered
                # this works because we cannot cluster points twice and it makes
                # the search space smaller (at the expense of rebuilding the tree and
                # added code complexity for offset)
                unclustered_points, index_map = [], {}
                for i, point in enumerate(self.points):
                    if i in clustered_points:
                        continue
                    index_map[len(unclustered_points)] = i
                    unclustered_points.append(point)
                if unclustered_points:
                    all_tree = KDTree(np.array(unclustered_points))

        if batch_points:
            clusters, clustered_points = self._greedy_cluster_batch(
                all_tree, index_map, batch_map, batch_points, clusters, clustered_points
            )
        self.clusters = clusters
        self.centroids = [self.points[i] for i in clusters.keys()]
        self.tree = KDTree(np.array(self.centroids))

    def _greedy_cluster_batch(self, all_tree, index_map, batch_map, batch_points,
                              clusters, clustered_points):
        query_tree = KDTree(np.array(batch_points))
        result = query_tree.query_ball_tree(all_tree, self.radius, eps=0.1)
        for i, pts in enumerate(result):
            index_in_all_points = batch_map[i]
            if index_in_all_points in clustered_points:
                continue
            clusters[index_in_all_points] = set([index_in_all_points])
            clustered_points.add(index_in_all_points)
            pts = {index_map[pt] for pt in pts}
            pts -= clustered_points
            clusters[index_in_all_points] |= pts
            clustered_points |= pts
        return clusters, clustered_points

    def _cluster_radius(self):
        all_dists = []
        for centroid, cluster in self.clusters.items():
            centroid, dists = self.raw[centroid], []
            for point in [self.raw[i] for i in cluster]:
                dists.append(needle_distance(centroid, point))
            all_dists.append(pd.Series(dists).quantile([0.5, 0.80, 0.95, 1]))
        all_quants = pd.DataFrame(all_dists).mean()
        return all_quants

    def to_dict(self):
        out = {}
        for centroid, points in self.clusters.items():
            out[self.raw[centroid]] = [self.raw[point] for point in points]
        return out

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
