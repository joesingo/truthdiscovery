import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm, PriorBelief
from truthdiscovery.output import Result


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

    def run(self, data):
        """
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        claim_counts = np.matmul(data.sc, np.ones((data.num_claims,)))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        for _ in range(self.num_iterations):
            investment_amounts = trust / claim_counts
            # Trust update can be expressed as the of entry-wise product of
            # investment amounts and the following matrix, which is obtained
            # by entry-wise division
            mat = data.sc / np.matmul(data.sc.T, investment_amounts)
            trust = investment_amounts * np.matmul(mat, belief)

            # Note: investment amounts recalculated
            belief = np.matmul(data.sc.T, trust / claim_counts) ** self.g

            trust = trust / max(trust)
            belief = belief / max(belief)

        return Result(
            trust=list(trust),
            belief=data.get_variable_value_beliefs(belief)
        )
