import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm
from truthdiscovery.output import Result


class TruthFinder(BaseIterativeAlgorithm):
    """
    TruthFinder by Yin, Han, Yu.
    """
    num_iterations = 200
    influence_param = 0.5
    dampening_factor = 0.3
    initial_trust = 0.9

    def __init__(self, *args, influence_param=None, dampening_factor=None,
                 initial_trust=None, **kwargs):
        """
        :param influence_param:  A number in [0, 1] that controls how much
                                 influence related claims have on confidence
                                 scores (ro in the paper)
        :param dampening_factor: A number in (0, 1) that prevents overly high
                                 confidence when sources are not independent
                                 (gamma in the paper)
        :param initial_trust:    Initial trust value for each source
        """
        if influence_param is not None:
            self.influence_param = influence_param
        if dampening_factor is not None:
            self.dampening_factor = dampening_factor
        if initial_trust is not None:
            self.initial_trust = initial_trust
        super().__init__(*args, **kwargs)

    @classmethod
    def get_log_trust(cls, trust):
        """
        Return the 'tau' vector as defined in the TruthFinder paper. This
        involves taking logs to convert trust in [0, 1] to [0, +inf) to prevent
        numerical underflow
        :param trust: numpy array of trust values
        :return:      tau vector
        """
        return -np.log(1 - trust)

    def run(self, data):
        """
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        trust = np.zeros((data.num_sources,))
        try:
            imp = data.imp
        except AttributeError:
            imp = np.zeros((data.num_claims, data.num_claims))

        a_mat = (data.sc.T / np.matmul(data.sc, np.ones((data.num_claims),))).T
        b_mat = data.sc.T + self.influence_param * np.matmul(imp.T, data.sc.T)

        trust = np.full((data.num_sources,), self.initial_trust)
        belief = np.zeros((data.num_claims,))

        # TODO: implement running until convergence using cosine similarilty,
        # as per the TruthFinder paper
        for _ in range(self.num_iterations):
            log_belief = np.matmul(b_mat, self.get_log_trust(trust))
            belief = 1 / (1 + np.exp(-self.dampening_factor * log_belief))
            trust = np.matmul(a_mat, belief)

        return Result(
            trust=list(trust),
            belief=data.get_variable_value_beliefs(belief)
        )