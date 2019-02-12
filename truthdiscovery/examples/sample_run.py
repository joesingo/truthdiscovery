"""
Script to demonstrate running an algorithm on some small made-up data
"""
import numpy.ma as ma

from truthdiscovery.algorithm import AverageLog
from truthdiscovery.input import Dataset


if __name__ == "__main__":
    data = Dataset(ma.masked_values([
        [1, 4, 0, 5, 7, 0],
        [0, 2, 0, 4, 9, 0],
        [1, 0, 2, 3, 8, 4],
        [4, 0, 2, 5, 0, 0],
        [4, 0, 3, 3, 4, 4]
    ], 0))
    alg = AverageLog()
    results = alg.run(data)
    print("trust scores:")
    for source, trust_val in enumerate(results.trust):
        print("  source {}: {:.3f}".format(source, trust_val))
    print("")
    print("belief scores:")
    for var, beliefs in enumerate(results.belief):
        print("  variable {}:".format(var))
        for val in sorted(beliefs):
            print("    {}: {:.3f}".format(val, beliefs[val]))
