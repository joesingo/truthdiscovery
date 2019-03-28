import sys

import numpy.ma as ma

from truthdiscovery.algorithm import *
from truthdiscovery.input import *
from truthdiscovery.graphs import *
from truthdiscovery.utils import ConvergenceIterator, DistanceMeasures


if __name__ == "__main__":
    try:
        out_path = sys.argv[1]
    except IndexError:
        print("usage: {} DEST".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

#     tuples = [
#         ("source 1", "x", 4),
#         ("source 1", "y", 7),
#         ("source 2", "y", 7),
#         ("source 2", "z", 5),
#         ("source 3", "x", 3),
#         ("source 3", "z", 5),
#         ("source 4", "x", 3),
#         ("source 4", "y", 6),
#         ("source 4", "z", 8)
#     ]
#     mydata = Dataset(tuples)

    mydata = MatrixDataset(ma.masked_values([
        [1, 9, 3, 4],
        [2, 2, 9, 9],
        [9, 9, 7, 9],
        [1, 2, 5, 9]
    ], 9))

    it = ConvergenceIterator(DistanceMeasures.L2, 0.001)
    algorithm = Investment(iterator=it)

    cs = ResultsGradientColourScheme(algorithm.run(mydata))
    rend = MatrixDatasetGraphRenderer(zero_indexed=False, colours=cs)
    with open(out_path, "wb") as outfile:
        rend.draw(mydata, outfile)
    # animator = Animator(renderer=rend, frame_duration=0.2)
    # with open(out_path, "wb") as outfile:
    #     animator.animate(outfile, algorithm, mydata)
