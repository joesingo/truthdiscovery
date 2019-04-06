"""
Compare the speed of convergence for iterative algorithms.

This script runs iterative algorithms on a large synthetic dataset, and records
the distance between old and new trust vectors at each iteration. This is
repeated for each of the available distance measures.

These distances are then plotted, so that the convergence (or otherwise) of
each algorithm can be compared.
"""
from io import StringIO
from os import path
import sys

import matplotlib.pyplot as plt

from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    PooledInvestment,
    Sums,
    TruthFinder
)
from truthdiscovery.input import SupervisedData
from truthdiscovery.utils import ConvergenceIterator, DistanceMeasures
from truthdiscovery.exceptions import ConvergenceError


DATA_CSV = path.join(path.dirname(__file__), "large_synthetic_data.csv")
ALGORITHMS = [Sums, AverageLog, Investment, PooledInvestment, TruthFinder]
MEASURE_NAMES = {
    DistanceMeasures.L1: "$L_1$ norm",
    DistanceMeasures.L2: "$L_2$ norm",
    DistanceMeasures.L_INF: r"$L_{\infty}$ norm",
    DistanceMeasures.COSINE: "1 - cosine similarity"
}


def main(csv_file):
    """
    Perform the test
    """
    print("Loading data...")
    sup = SupervisedData.from_csv(csv_file)
    fig, axes = plt.subplots(2, 2)
    plt.subplots_adjust(hspace=0.3)
    fig.suptitle(
        "Convergence of various algorithms using different distance measures "
        "(synthetic data with {d.num_sources} sources, {d.num_variables} "
        "variables)".format(d=sup.data)
    )
    subplot_coords = ([0, 0], [0, 1], [1, 0], [1, 1])

    for measure, (row, col) in zip(DistanceMeasures, subplot_coords):
        distances = {}

        iterator = ConvergenceIterator(measure, 0, limit=30, debug=True)
        for cls in ALGORITHMS:
            name = cls.__name__
            print("running {} using {} measure".format(name, measure))
            alg = cls(iterator=iterator)
            stdout = StringIO()
            sys.stdout = stdout
            try:
                _res = alg.run(sup.data)
                print(
                    "finished in {} iterations".format(alg.iterator.it_count),
                    file=sys.stderr
                )
            except ConvergenceError:
                print("{} did not converge with {} measure!"
                      .format(name, measure),
                      file=sys.stderr)
            finally:
                sys.stdout = sys.__stdout__

            distances[name] = []
            for line in stdout.getvalue().split("\n"):
                if not line:
                    continue
                _, dist = line.split(",")
                distances[name].append(float(dist))

        max_its = max(len(dists) for dists in distances.values())
        x = range(1, max_its + 1)

        ax = axes[row, col]
        ax.set_title("{}".format(MEASURE_NAMES[measure]))
        ax.set_xlabel("Iteration number")
        ax.set_ylabel("Distance between old and new trust (log scale)")
        for name, dists in distances.items():
            while len(dists) < max_its:
                dists.append(None)
            ax.semilogy(x, dists, label=name, linewidth=3)
        ax.legend()
    plt.show()


if __name__ == "__main__":
    with open(DATA_CSV) as csv_file:
        main(csv_file)
