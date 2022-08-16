import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm


class CRH(BaseIterativeAlgorithm):
    """
    An instance of the CRH algorithm from Yaliang Li et. al.
    """
    eps = 1e-5

    def __init__(self, *args, eps=None, **kwargs):
        """
        :param: eps: A small positive constant used to ensure arguments to
                     logarithms are positive, and to avoid potential division
                     by zero
        """
        if eps is not None:
            self.eps = eps
        super().__init__(*args, **kwargs)

    def _run(self, data):
        trust = np.zeros((data.num_sources,))
        belief = ((data.sc.T @ np.ones((data.num_sources,)))
                  / data.num_sources)
        i = np.eye(data.num_claims)
        while not self.iterator.finished():
            t = np.tile(belief, (data.num_claims, 1))
            y = (t - i) ** 2
            z = data.mut_ex.toarray() * y
            alpha = self.eps + data.sc @ z @ np.ones((data.num_claims,))
            new_trust = self.eps - np.log(alpha / np.sum(alpha))
            belief = (data.sc.T @ new_trust) / np.sum(new_trust)

            self.iterator.compare(trust, new_trust)
            trust = new_trust
            self.log(data, trust, belief)

        return trust, belief
