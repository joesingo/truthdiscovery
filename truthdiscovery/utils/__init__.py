from truthdiscovery.utils.iterator import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator,
    Iterator
)


def filter_dict(dct, keys):
    """
    :yield: Tuples ``(key, value)`` for keys in ``keys``
    """
    for key in keys:
        try:
            yield (key, dct[key])
        except KeyError:
            pass
