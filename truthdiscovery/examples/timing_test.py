"""
Script to measure run-time of various algorithms
"""
from collections import OrderedDict
import json
from os import path
import sys

import numpy as np
import matplotlib.pyplot as plt

from truthdiscovery.input import MatrixDataset, SyntheticData
from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    Sums,
    TruthFinder
)

DATA_SIZES = list(range(100, 2001, 200))
FIXED_SIZE = 500
CLAIM_PROBABILITY = 0.1
DOMAIN_SIZE = 4

ALGORITHMS = OrderedDict({
    "voting": MajorityVoting(),
    "sums": Sums(),
    "average.log": AverageLog(),
    "investment": Investment(),
    "Pooled Investment": PooledInvestment(),
    "TruthFinder": TruthFinder()
})


def generate_timings():
    print("generating large trust vector...", file=sys.stderr)
    max_size = max(DATA_SIZES)
    trust = np.random.uniform(size=(max_size,))

    print("generating large dataset...", file=sys.stderr)
    large_synth = SyntheticData(
        trust,
        num_variables=max_size,
        claim_probability=CLAIM_PROBABILITY,
        domain_size=DOMAIN_SIZE
    )
    sv = large_synth.data.sv

    vary_sources_shapes = [(n, FIXED_SIZE) for n in DATA_SIZES]
    vary_vars_shapes = [(FIXED_SIZE, n) for n in DATA_SIZES]

    results = {
        "fixed_size": FIXED_SIZE,
        "vary_num_sources": perform_test(sv, vary_sources_shapes),
        "vary_num_vars": perform_test(sv, vary_vars_shapes)
    }
    print(json.dumps(results))


def perform_test(master_sv, data_shapes):
    """
    Perform a number of timing tests

    :param master_sv:   source-variabels matrix to extract smaller datasets
                        from
    :param data_shapes: an iterable of (num_sources, num_variables) for the
                        sizes of data to test with
    :return: an OrderedDict {alg_label: list_of_timings, ...}
    """
    timings = OrderedDict()
    for num_sources, num_vars in data_shapes:
        print(
            "getting reduced dataset: {} sources, {} variables..."
            .format(num_sources, num_vars),
            file=sys.stderr
        )
        data = MatrixDataset(master_sv[0:num_sources, 0:num_vars])

        for alg_label, alg in ALGORITHMS.items():
            print("  running {}...".format(alg_label), end="", file=sys.stderr)
            res = alg.run(data)
            print(" {:.3f} seconds".format(res.time_taken), file=sys.stderr)

            if alg_label not in timings:
                timings[alg_label] = []
            timings[alg_label].append(res.time_taken)
    return timings


def plot_results(timings):
    fig, axes = plt.subplots(1, 2)
    vary_sources_ax, vary_vars_ax = axes

    # Set titles and axis labels
    fig.suptitle(
        "Run time of algorithms on synthetic datasets of increasing size"
    )
    vary_sources_ax.set_title(
        "Run time as number of sources increases (number of variables fixed "
        "at {})".format(timings["fixed_size"])
    )
    vary_sources_ax.set_xlabel("Number of sources")
    vary_sources_ax.set_ylabel("Run time (seconds)")
    vary_vars_ax.set_title(
        "Run time as number of variables increases (number of sources fixed "
        "at {})".format(timings["fixed_size"])
    )
    vary_vars_ax.set_xlabel("Number of variables")
    vary_vars_ax.set_ylabel("Run time (seconds)")

    configurations = [
        (vary_sources_ax, "vary_num_sources"),
        (vary_vars_ax, "vary_num_vars")
    ]
    for ax, test_label in configurations:
        for alg_label, results in timings[test_label].items():
            ax.plot(
                DATA_SIZES, results, "o-", label=alg_label.capitalize(),
                linewidth=3
            )
        ax.legend()
    fig.tight_layout()
    plt.show()


def usage():
    print("usage: {} (generate | plot RESULTS)".format(sys.argv[0]),
          file=sys.stderr)
    print("generate timing results as JSON and print to stdout, or plot"
          "results from a JSON file", file=sys.stderr)


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    if sys.argv[1] == "generate":
        generate_timings()
    elif sys.argv[1] == "plot" and len(sys.argv) >= 3:
        with open(sys.argv[2]) as jsonfile:
            plot_results(json.load(jsonfile))
    else:
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
