"""
Script to run various experiments measuring the accuracy of algorithms on
synthetic datasets, and graphing results
"""
from collections import OrderedDict
import itertools
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

from truthdiscovery.input import SyntheticData
from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    Sums,
    TruthFinder
)


ALGORITHMS = OrderedDict({
    "Voting": MajorityVoting(),
    "Sums": Sums(),
    "Average.Log": AverageLog(),
    "Investment": Investment(),
    "Pooled Investment": PooledInvestment(),
    "TruthFinder": TruthFinder()
})


class Experiment:
    # labels for values of independent variable
    labels = None
    # dict mapping algorithm labels to objects
    algorithms = None
    # number of trials to perform for each value
    reps = 10
    # parameters to pass to synthetic data generation. Value for independent
    # variable should be an iterable of values of callables
    synth_params = None

    def __init__(self):
        for key, val in self.synth_params.items():
            # If not an iterable, repeat the value endlessly
            try:
                self.synth_params[key] = iter(val)
            except TypeError:
                self.synth_params[key] = itertools.repeat(val)

    def run(self):
        out = {}
        for var_label in self.labels:
            # results dict: {alg_label: [acc, ...], ...}
            results = {}
            params = dict(self.get_synth_params())
            for _ in range(self.reps):
                this_params = {}
                for key, val in params.items():
                    try:
                        this_params[key] = val()
                    except TypeError:
                        this_params[key] = val

                synth = SyntheticData(**this_params)
                for alg_label, alg in self.algorithms.items():
                    acc = synth.get_accuracy(alg.run(synth.data))
                    this_res = results.setdefault(alg_label, [])
                    this_res.append(acc)
            out[var_label] = results
        return out

    def get_synth_params(self):
        def inner():
            for key, seq in self.synth_params.items():
                val = next(seq)
                yield key, val
        return dict(inner())

    @classmethod
    def run_multiple(cls, *args):
        out = {}
        for exp in args:
            name = exp.__class__.__name__
            print("running {}...".format(name), file=sys.stderr)
            out[name] = exp.run()
        return out

    @classmethod
    def graph(cls, res):
        raise NotImplementedError


class TrustDistExperiment(Experiment):
    algorithms = ALGORITHMS
    labels = None  # set in constructor
    num_sources = 100
    synth_params = {
        "num_variables": 100,
        "claim_probability": 0.1,
        "domain_size": 5,
        "trust": None  # set in constructor
    }

    def __init__(self):
        trust_dists = OrderedDict({
            "Mostly Bad": np.array(list(
                0.75 if i < self.num_sources / 3 else 0.25
                for i in range(self.num_sources)
            )),
            "Uniform": lambda: np.random.uniform(size=(self.num_sources,)),
            r"Normal ($\mu=0.5$, $\sigma=0.15$)": lambda: np.clip(
                np.random.normal(0.5, 0.15, size=(self.num_sources,)),
                0, 1
            ),
        })
        self.labels = trust_dists.keys()
        self.synth_params["trust"] = trust_dists.values()
        super().__init__()

    @classmethod
    def graph(cls, res):
        # Plot trust experiment as bar chart
        fig, ax = plt.subplots()
        num_trust_dists = len(res)
        bar_width = 0.8 / num_trust_dists
        alg_labels = list(cls.algorithms.keys())
        index = np.arange(len(alg_labels))
        for i, (dist, results) in enumerate(res.items()):
            # Get mean accuracy scores for all algorithms for this trust
            # distribution
            acc_scores = list(np.mean(results[alg]) for alg in alg_labels)
            ax.bar(
                index + i * bar_width,
                acc_scores,
                bar_width,
                align="edge",
                label=dist
            )

        ax.set_title(
            "Source trust distribution experiment ({} sources, {} variables, "
            "{} domain values)"
            .format(cls.num_sources, cls.synth_params["num_variables"],
                    cls.synth_params["domain_size"])
        )
        ax.set_xlabel("Algorithm")
        ax.set_ylabel("Mean accuracy over {} trials".format(cls.reps))
        ax.set_xticks(index + bar_width * num_trust_dists / 2)
        ax.set_xticklabels(alg_labels)
        ax.legend()
        fig.tight_layout()


class ClaimDensityExperiment(Experiment):
    labels = None  # set in constructor
    algorithms = ALGORITHMS
    synth_params = {
        "trust": lambda: np.random.uniform(size=(100,)),
        "num_variables": 100,
        "claim_probability": None,  # set in constructor
        "domain_size": 10
    }

    def __init__(self):
        claim_probs = list(np.clip(np.arange(0.1, 1.025, 0.05), 0, 1))
        self.synth_params["claim_probability"] = claim_probs
        self.labels = claim_probs
        super().__init__()

    @classmethod
    def graph(cls, res):
        _fig, ax = plt.subplots()
        # JSON does not support non-string keys, so convert to float
        xs = list(map(float, res.keys()))
        for alg in cls.algorithms:
            ys = [np.mean(res[str(x)][alg]) for x in xs]
            ax.plot(xs, ys, "x-", label=alg, linewidth=3)

        ax.set_title(
            "Claim probability experiment ({} sources, {} variables, {} "
            "domain values)"
            .format(100, cls.synth_params["num_variables"],
                    cls.synth_params["domain_size"])
        )
        ax.set_xlabel("Claim probability")
        ax.set_ylabel("Mean accuracy over {} trials".format(cls.reps))
        ax.legend()


class DomainSizeExperiment(Experiment):
    labels = None
    algorithms = ALGORITHMS
    synth_params = {
        "trust": lambda: np.random.uniform(size=(100,)),
        "num_variables": 100,
        "claim_probability": 0.1,
        "domain_size": None
    }

    def __init__(self):
        domain_sizes = list(range(2, 21))
        self.labels = domain_sizes
        self.synth_params["domain_size"] = domain_sizes
        super().__init__()

    @classmethod
    def graph(cls, res):
        _fig, ax = plt.subplots()
        xs = list(map(int, res.keys()))
        for alg in cls.algorithms:
            ys = [np.mean(res[str(x)][alg]) for x in xs]
            ax.plot(xs, ys, "x-", label=alg, linewidth=3)

        ax.set_title(
            "Domain size experiment ({} sources, {} variables, {} "
            "claim probability)"
            .format(100, cls.synth_params["num_variables"],
                    cls.synth_params["claim_probability"])
        )
        ax.set_xlabel("Variable domain size")
        ax.set_ylabel("Mean accuracy over {} trials".format(cls.reps))
        ax.legend()


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print("usage: {}".format(sys.argv[0]))
        print("       {} graph FILE\n".format(sys.argv[0]))
        print("in the first form, run the experiment and print results as "
              "JSON to stdout")
        print("in the second, graph the results from the given file")
        return

    if len(sys.argv) >= 3 and sys.argv[1] == "graph":
        with open(sys.argv[2]) as json_file:
            res = json.load(json_file)
        for cls_name, results in res.items():
            globals()[cls_name].graph(results)
        plt.show()
        return

    res = Experiment.run_multiple(
        # ClaimDensityExperiment(),
        # TrustDistExperiment(),
        DomainSizeExperiment()
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
