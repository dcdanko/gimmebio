
import pandas as pd


def entropy_reduce_position_matrix(original, r, metric, centroids=set(), sep=',', logger=None):
    """Return an Entropy Reduced version of the input matrix.

    Return a pandas dataframe with a subset of columns from the
    original dataframe with the guarantee that every column in
    the original dataframe is within `r` of at least one column
    in the reduced frame*.

    * Exclude all columns with sum == 0

    Optionally pass a logger function which will get
    (num_centroids, num_columns_processed) pairs
    """
    for i, (col_name, col) in enumerate(original.iteritems()):
        if logger:
            logger(len(centroids), i)
        if col.sum() == 0:
            continue
        new_centroid = True
        for centroid_col_name in centroids:
            d = metric(original[centroid_col_name], col)
            if d <= r:
                new_centroid = False
                continue
        if new_centroid:
            centroids.add(col_name)
    return original[centroids]


def entropy_reduce_postion_matrices(filehandles, r, metric, sep=',', logger=None):

    matrix = entropy_reduce_position_matrix(filehandles[0], r, metric, sep=sep, logger=logger)
    centroids = set(matrix.columns)
    for fhandle in filehandles[1:]:
        pass
