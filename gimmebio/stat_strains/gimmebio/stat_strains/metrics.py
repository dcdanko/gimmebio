

def scaling_manhattan(x1, x2):
    x1 = x1 / x1.sum()
    x2 = x2 / x2.sum()
    diff = (x1 - x2).abs().sum()
    return diff
