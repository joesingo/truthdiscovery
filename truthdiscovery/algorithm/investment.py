import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm, PriorBelief


class Investment(BaseIterativeAlgorithm):
    """
    Investment by Pasternack and Roth.

    Sources invest uniformly in their claims and receive returns; the source
    who invested most in claim j received the most return from claim j
    """
    priors = PriorBelief.VOTED
    g = 1.2

    def __init__(self, *args, g=None, **kwargs):
        if g is not None:
            self.g = g
        super().__init__(*args, **kwargs)

    def _run(self, data):
        claim_counts = np.matmul(data.sc, np.ones((data.num_claims,)))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        while not self.iterator.finished():
            investment_amounts = trust / claim_counts
            # Trust update can be expressed as the of entry-wise product of
            # investment amounts and the following matrix, which is obtained
            # by entry-wise division
            mat = data.sc / np.matmul(data.sc.T, investment_amounts)
            new_trust = investment_amounts * np.matmul(mat, belief)

            # Note: investment amounts recalculated
            belief = np.matmul(data.sc.T, new_trust / claim_counts) ** self.g

            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(new_trust, trust)
            trust = new_trust

        return trust, belief
