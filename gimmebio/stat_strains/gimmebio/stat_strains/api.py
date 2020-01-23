
import pandas as pd
from multiprocessing import Pool
from scipy.spatial.distance import cdist, pdist


def entropy_reduce_position_matrix(
    original, r, metric,
    min_fill=2, centroids=None, sep=',', logger=None
    ):
    """Return an Entropy Reduced version of the input matrix.

    Return a pandas dataframe with a subset of columns from the
    original dataframe with the guarantee that every column in
    the original dataframe is within `r` of at least one column
    in the reduced frame*.

    * Exclude all columns with sum == 0

    Optionally pass a logger function which will get
    (num_centroids, num_columns_processed) pairs
    """
    if not centroids:
        centroids = list()
    for i, (col_name, col) in enumerate(original.iteritems()):
        if logger:
            logger(len(centroids), i)
        if (col > 0).sum() < min_fill:
            continue
        if len(centroids) == 0:
            centroids.append(col_name)
            continue
        d = min(cdist(
            pd.DataFrame(original[centroids]).T,
            pd.DataFrame(original[col_name]).T,
            metric=metric
        ))
        if d > r:
            centroids.append(col_name)
    return original[centroids]


def parse_matrix_default(filehandle):
    return pd.read_csv(filehandle, index_col=0, header=0)


def entropy_reduce_postion_matrices(
    filehandles, r, metric, min_fill=2, sep=',',
    logger=None, matrix_parser=parse_matrix_default
    ):
    if logger:
        logger(filehandles[0])
    matrix = matrix_parser(filehandles[0])
    matrix = entropy_reduce_position_matrix(
        matrix, r, metric, min_fill=min_fill, sep=sep
    )
    for fhandle in filehandles[1:]:
        if logger:
            logger(fhandle)
        centroids = list(matrix.columns)
        new_matrix = matrix_parser(fhandle)
        matrix = pd.concat([matrix, new_matrix], axis=1, sort=False)
        matrix = entropy_reduce_position_matrix(
            matrix, r, metric,
            centroids=centroids,
            min_fill=min_fill, sep=sep
        )
    return matrix


class ReducingMatrix:

    def __init__(self, matrix, metric, r):
        self.metric = metric
        self.r = r
        self.matrix = matrix
        self.cur_matrix = None

    def _add_one_col(self, col_name):
        col = self.cur_matrix[col_name]
        new_centroid = True
        for _, centroid in self.matrix.iteritems():
            d = self.metric(centroid, col)
            if d <= self.r:
                new_centroid = False
                continue
        return col_name, new_centroid

    def add_new_matrix(self, new_matrix, pool):
        self.cur_matrix = new_matrix
        new_centroids = {
            col_name
            for col_name, centroid in pool.imap_unordered(
                self._add_one_col,
                new_matrix.columns,
                chunksize=min(1000, new_matrix.shape[1])
            )
            if centroid
        }
        self.matrix = pd.concat(
            [self.matrix, new_matrix[new_centroids]],
            axis=1, sort=False
        )
        return self.matrix


def fast_reduce_one_matrix(matrix, new_matrix, metric, r):
    all_cols = set(matrix.columns) | set(new_matrix.columns)
    for col_name in all_cols - set(matrix.columns):
        matrix[col_name] = 0
    for col_name in all_cols - set(new_matrix.columns):
        new_matrix[col_name] = 0
    dists = pd.DataFrame(cdist(matrix, new_matrix, metric=metric))
    new_centroids = set()
    for ind, dists in dists.iteritems():
        if dists.min() > r:
            new_centroids.add(ind)
    new_centroids = new_matrix.index[list(new_centroids)]
    return new_centroids


def fast_entropy_reduce_postion_matrices(
    filehandles, r, metric, sep=',',
    logger=None, matrix_parser=parse_matrix_default,
    ):
    if logger:
        logger(filehandles[0])
    matrix = matrix_parser(filehandles[0]).T

    for fhandle in filehandles[1:]:
        if logger:
            logger(fhandle)
        new_matrix = matrix_parser(fhandle).T
        new_centroids = fast_reduce_one_matrix(
            matrix, new_matrix, metric, r
        )
        matrix = pd.concat(
            [
                matrix,
                new_matrix.loc[new_centroids]
            ],
            axis=0, sort=False
        )
    return matrix.T


def parallel_entropy_reduce_postion_matrices(
    filehandles, r, metric, min_fill=2, sep=',',
    logger=None, matrix_parser=parse_matrix_default,
    threads=1
    ):
    if logger:
        logger(filehandles[0])
    rmatrix = ReducingMatrix(
        matrix_parser(filehandles[0]),
        metric,
        r,
    )
    with Pool(threads) as pool:
        for fhandle in filehandles[1:]:
            if logger:
                logger(fhandle)
            rmatrix.add_new_matrix(matrix_parser(fhandle), pool)
    return rmatrix.matrix
