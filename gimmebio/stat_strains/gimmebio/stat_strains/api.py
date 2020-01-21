
import pandas as pd


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
        centroids = set()
    for i, (col_name, col) in enumerate(original.iteritems()):
        if logger:
            logger(len(centroids), i)
        if (col > 0).sum() < min_fill:
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
        centroids = set(matrix.columns)
        new_matrix = matrix_parser(fhandle)
        matrix = pd.concat([matrix, new_matrix], axis=1, sort=False)
        matrix = entropy_reduce_position_matrix(
            matrix, r, metric,
            centroids=centroids,
            min_fill=min_fill, sep=sep
        )
    return matrix
