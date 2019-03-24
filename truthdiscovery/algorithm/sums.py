import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm


class Sums(BaseIterativeAlgorithm):
    """
    Sums, or Hubs and Authorities, algorithm.

    Described by Kleinberg for web pages, and adapted to truth-discovery by
    Pasternack and Roth
    """
    def _run(self, data):
        trust = np.zeros((data.num_sources,))
        belief = self.get_prior_beliefs(data)
        self.log(data, trust, belief)

        while not self.iterator.finished():
            new_trust = data.sc @ belief
            belief = data.sc.T @ new_trust

            # Trust and belief are normalised so that the largest entries in
            # each are 1; otherwise trust and belief scores grow without bound
            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(trust, new_trust)
            trust = new_trust
            self.log(data, trust, belief)

        return trust, belief
