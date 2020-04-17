
from functools import lru_cache


def isint(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


@lru_cache(maxsize=1000)
def caching_get_sample(lib, sample_name):
    sample = lib.sample(sample_name).idem()
    return sample


@lru_cache(maxsize=1000)
def caching_get_sample_ar(sample, module_name):
    ar = sample.analysis_result(module_name).idem()
    return ar
