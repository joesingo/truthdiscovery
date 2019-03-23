"""
Example script to produce a PNG image for a graph representation of a dataset
"""
import sys

from truthdiscovery.algorithm import Sums
from truthdiscovery.input import Dataset
from truthdiscovery.visual import GraphRenderer, ResultsGradientColourScheme


if __name__ == "__main__":
    try:
        outpath = sys.argv[1]
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
    results = Sums().run(mydata)

    colour_scheme = ResultsGradientColourScheme(results)
    renderer = GraphRenderer(
        mydata, width=1000, height=700, colours=colour_scheme
    )
    with open(outpath, "wb") as imgfile:
        renderer.draw(imgfile)
