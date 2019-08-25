

class GreedyRadialCover:

    def __init__(self, metric, radius):
        self.metric = metric
        self.r = radius
        self.clusters = {}

    def add(self, kmer):
        for center in self.clusters.keys():
            if self.metric(center, kmer) <= self.r:
                self.clusters[center].add(kmer)
                return
        self.clusters[kmer] = set([kmer])

    def search(self, kmer, max_dist):
        hits = set()
        for center, members in self.clusters.items():
            if self.metric(center, kmer) > (max_dist + self.r):
                continue
            for other_kmer in members:
                if self.metric(other_kmer, kmer) <= max_dist:
                    hits.add(other_kmer)
        return hits

    def stats(self):
        return {
            'num_kmers': sum([len(clust) for clust in self.clusters.values()]),
            'num_singletons': sum([
                1 if len(clust) == 1 else 0 for clust in self.clusters.values()
            ]),
            'num_clusters': len(self.clusters),
        }
