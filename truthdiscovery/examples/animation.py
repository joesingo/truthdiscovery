import sys

from truthdiscovery.algorithm import *
from truthdiscovery.input import Dataset
from truthdiscovery.graphs import Animator, GraphRenderer
from truthdiscovery.utils import ConvergenceIterator, DistanceMeasures


if __name__ == "__main__":
    try:
        out_path = sys.argv[1]
    except IndexError:
        print("usage: {} DEST".format(sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    tuples = [
        ("source 1", "x", 4),
        ("source 1", "y", 7),
        ("source 2", "y", 7),
        ("source 2", "z", 5),
        ("source 3", "x", 3),
        ("source 3", "z", 5),
        ("source 4", "x", 3),
        ("source 4", "y", 6),
        ("source 4", "z", 8)
    ]
    mydata = Dataset(tuples)

    # it = ConvergenceIterator(DistanceMeasures.L2, 0.001)
    # algorithm = Investment(iterator=it)
    algorithm = Investment()

    rend = GraphRenderer()
    animator = Animator(renderer=rend, frame_duration=0.2)
    with open(out_path, "wb") as outfile:
        animator.animate(outfile, algorithm, mydata)
