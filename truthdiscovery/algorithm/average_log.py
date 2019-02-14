import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm


class AverageLog(BaseIterativeAlgorithm):
    """
    AverageLog by Pasternack and Roth.

    Similar to Sums (and uses the same belief update step), but updates source
    trust as average claim belief weighted by log(number of claims).
    """
    def _run(self, data):
        trust = np.zeros((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        # Pre-compute the number of claims made by each source and log
        # weighting, since this is used in each iteration and does not change.
        # Note that the number of claims made by s_i is the sum of the i-th row
        # of the claims matrix, so we multiply by [1 ... 1].T to get the counts
        # for all sources in one operation
        claim_counts = np.matmul(data.sc, np.ones((data.num_claims,)))

        # TODO: decide how to handle this case better
        if np.any(claim_counts == 0):
            raise ValueError("All sources must make at least one claim")

        weights = np.log(claim_counts) / claim_counts

        while not self.iterator.finished():
            # Entry-wise multiplication
            new_trust = weights * np.matmul(data.sc, belief)
            belief = np.matmul(data.sc.T, new_trust)

            # Normalise as with sums
            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(new_trust, trust)
            trust = new_trust

        return trust, belief
