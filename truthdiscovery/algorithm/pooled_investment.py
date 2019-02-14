import numpy as np

from truthdiscovery.algorithm.base import PriorBelief
from truthdiscovery.algorithm.investment import Investment
from truthdiscovery.utils.iterator import FixedIterator


class PooledInvestment(Investment):
    """
    PooledInvestment by Pasternack and Roth.

    Refinement of Investment that makes use of mutual exclusion amongst claims
    """
    g = 1.4
    priors = PriorBelief.UNIFORM

    def get_default_iterator(self):
        """
        Override the default iterator to perform only 10 iterations
        """
        return FixedIterator(10)

    def _run(self, data):
        claim_counts = np.matmul(data.sc, np.ones((data.num_claims,)))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        while not self.iterator.finished():
            # Trust update is the same as for Investment
            investment_amounts = trust / claim_counts
            mat = data.sc / np.matmul(data.sc.T, investment_amounts)
            new_trust = investment_amounts * np.matmul(mat, belief)

            # 'Invest' trust in claims, grow with non-linear function, and
            # update belief
            base_returns = np.matmul(data.sc.T, (new_trust / claim_counts))
            returns = base_returns ** self.g
            belief = base_returns * (returns / np.matmul(data.mut_ex, returns))

            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(new_trust, trust)
            trust = new_trust

        return trust, belief
