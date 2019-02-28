import numpy as np

from truthdiscovery.algorithm.base import PriorBelief
from truthdiscovery.exceptions import EarlyFinishError
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
        claim_counts = data.sc @ np.ones((data.num_claims,))
        trust = np.ones((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        while not self.iterator.finished():
            # Trust update is the same as for Investment
            try:
                new_trust = self.update_trust(
                    trust, claim_counts, data.sc, belief
                )
            except EarlyFinishError:  # pragma: no cover
                break
            # 'Invest' trust in claims, grow with non-linear function, and
            # update belief
            base_returns = data.sc.T @ (new_trust / claim_counts)
            returns = base_returns ** self.g
            belief = base_returns * (returns / (data.mut_ex @ returns))

            new_trust = new_trust / max(new_trust)
            belief = belief / max(belief)

            self.iterator.compare(new_trust, trust)
            trust = new_trust

        return trust, belief
