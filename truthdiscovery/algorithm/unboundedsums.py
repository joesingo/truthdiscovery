import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm, PriorBelief
from truthdiscovery.utils.iterator import OrdinalConvergenceIterator


class UnboundedSums(BaseIterativeAlgorithm):
    """
    Our modification of Sums, described in the paper "An Axiomatic Approach to
    Truth Discovery" (forthcoming, at the time of writing)
    """
    priors = PriorBelief.COUNT

    def get_default_iterator(self):
        return OrdinalConvergenceIterator()

    def _run(self, data):
        trust = np.zeros((data.num_sources,))
        belief = self.get_prior_beliefs(data)
        self.log(data, trust, belief)

        while not self.iterator.finished():
            new_trust = data.sc @ belief
            belief = data.sc.T @ new_trust
            self.iterator.compare(trust, new_trust)
            trust = new_trust
            if np.max(trust) > 1000:
                trust /= 1000
            if np.max(belief) > 1000:
                belief /= 1000
            self.log(data, trust, belief)

        # convert (potentially very large) scores to ranking vectors
        rtrust = self.iterator.get_ranking_vector(trust)
        rbelief = self.iterator.get_ranking_vector(belief)
        return rtrust, rbelief
