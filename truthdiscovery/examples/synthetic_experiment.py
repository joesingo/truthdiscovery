"""
Small script to run various algorithms on synthetic datasets, calculate average
accuracy, and produce graphs with results.
"""
from collections import OrderedDict

import numpy as np
import matplotlib.pyplot as plt

from truthdiscovery.input import SyntheticDataset
from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    Sums
)


NUM_SOURCES = 100
NUM_VARIABLES = 100
CLAIM_PROBABILITY = 0.1
DOMAIN_SIZE = 4
REPETITIONS = 25


def main():
    trust_distributions = OrderedDict({
        # "fixed-0.25": lambda size: np.full(size, 0.25),
        # "fixed-0.5": lambda size: np.full(size, 0.5),
        # "fixed-0.75": lambda size: np.full(size, 0.75),
        # "fixed-range": lambda size: np.linspace(0, 1, num=size[0]),
        "mostly bad": lambda size: np.array(list(
            0.75 if i < size[0] / 3 else 0.25 for i in range(size[0])
        )),
        "uniform": np.random.uniform,
        r"normal ($\mu=0.5$, $\sigma=0.15$)": lambda size: np.random.normal(
            0.5, 0.15, size=size
        ),
    })
    algorithms = OrderedDict({
        "voting": MajorityVoting(),
        "sums": Sums(),
        "average.log": AverageLog(),
        "investment": Investment()
    })

    results = {}
    for dist_label, dist in trust_distributions.items():
        trust = np.clip(dist(size=(NUM_SOURCES,)), 0, 1)
        for _ in range(REPETITIONS):
            data = SyntheticDataset(
                trust, NUM_VARIABLES, CLAIM_PROBABILITY, DOMAIN_SIZE
            )

            for alg_label, alg in algorithms.items():
                acc = data.get_accuracy(alg.run(data))
                key = (alg_label, dist_label)
                if key not in results:
                    results[key] = []
                results[key].append(acc)

    for alg_label in algorithms:
        print("{}:".format(alg_label))
        for dist_label in trust_distributions:
            key = (alg_label, dist_label)
            mean = np.mean(results[key])
            print("  {}: {}".format(dist_label, mean))

    # Plot as barchart
    fig, ax = plt.subplots()
    bar_width = 0.8 / len(trust_distributions)
    index = np.arange(len(algorithms))
    for i, dist in enumerate(trust_distributions):
        # Get mean accuracy scores for all algorithms for this trust
        # distribution
        acc_scores = list(np.mean(results[(alg, dist)]) for alg in algorithms)
        ax.bar(
            index + i * bar_width,
            acc_scores,
            bar_width,
            align="edge",
            label=dist.capitalize()
        )

    ax.set_title("{} sources, {} variables, {} domain values".format(
        NUM_SOURCES, NUM_VARIABLES, DOMAIN_SIZE
    ))
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("Mean accuracy over {} trials".format(REPETITIONS))
    ax.set_xticks(index + bar_width * len(trust_distributions) / 2)
    ax.set_xticklabels(map(str.capitalize, algorithms.keys()))
    ax.legend()
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
