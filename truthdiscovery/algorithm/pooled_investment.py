import numpy as np

from truthdiscovery.algorithm.base import PriorBelief
from truthdiscovery.algorithm.investment import Investment
from truthdiscovery.output import Result


class PooledInvestment(Investment):
    """
    PooledInvestment by Pasternack and Roth.

    Refinement of Investment that makes use of mutual exclusion amongst claims
    """
    num_iterations = 10
    g = 1.4
    priors = PriorBelief.UNIFORM

    def run(self, data):
        """
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        claim_counts = np.matmul(data.sc, np.ones((data.num_claims,)))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        for _ in range(self.num_iterations):
            # Trust update is the same as for Investment
            investment_amounts = trust / claim_counts
            mat = data.sc / np.matmul(data.sc.T, investment_amounts)
            trust = investment_amounts * np.matmul(mat, belief)

            # 'Invest' trust in claims, grow with non-linear function, and
            # update belief
            base_returns = np.matmul(data.sc.T, (trust / claim_counts))
            returns = base_returns ** self.g
            belief = base_returns * (returns / np.matmul(data.mut_ex, returns))

            trust = trust / max(trust)
            belief = belief / max(belief)

        return Result(
            trust=list(trust),
            belief=data.get_variable_value_beliefs(belief)
        )
