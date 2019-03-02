import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm, PriorBelief
from truthdiscovery.exceptions import EarlyFinishError


class Investment(BaseIterativeAlgorithm):
    """
    Investment by Pasternack and Roth.

    Sources invest uniformly in their claims and receive returns; the source
    who invested most in a claim receives the most return from that claim
    """
    priors = PriorBelief.VOTED
    g = 1.2

    def __init__(self, *args, g=None, **kwargs):
        """
        :param g: exponent in non-linear function used to grow claim beliefs
                  at each iteration (optional)
        """
        if g is not None:
            self.g = g
        super().__init__(*args, **kwargs)

    def update_trust(self, old_trust, claim_counts, sc_mat, belief):
        """
        :return: an updated trust vector
        """
        # The amount each source has to invest in its claims
        investment_amounts = old_trust / claim_counts
        # The amount each claim receives in investment from its sources
        claim_investments = sc_mat.T @ investment_amounts
        if np.any(claim_investments == 0):
            raise EarlyFinishError(
                "Investment in at least one claim has become zero"
            )
        # Trust update can be expressed as the of entry-wise product of
        # investment amounts and the following matrix, which is obtained
        # by column-wise division (each column in sc is divided by the
        # corresponding entry in claim_investments)

        # (Note: using '/' here will result in a dense numpy array: we use
        # multiply() to get a sparse result instead)
        mat = sc_mat.multiply(1 / claim_investments)
        return investment_amounts * (mat @ belief)

    def _run(self, data):
        claim_counts = data.sc @ np.ones((data.num_claims,))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        while not self.iterator.finished():
            try:
                new_trust = self.update_trust(
                    trust, claim_counts, data.sc, belief
                )
            except EarlyFinishError:
                break
            belief = (data.sc.T @ (new_trust / claim_counts)) ** self.g

            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(new_trust, trust)
            trust = new_trust

        return trust, belief
