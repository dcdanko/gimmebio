

def memoize(func):
    """Memoize the input function."""
    tbl = {}

    def helper(args):
        if args not in tbl:
            tbl[args] = func(args)
        return tbl[args]
    return helper
