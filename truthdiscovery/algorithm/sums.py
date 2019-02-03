import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm
from truthdiscovery.output import Result


class Sums(BaseIterativeAlgorithm):
    """
    Sums, or Hubs and Authorities, algorithm.

    Described by Kleinberg for web pages, and adapted to truth-discovery by
    Pasternack and Roth
    """
    def run(self, data):
        """
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        trust = np.zeros((data.num_sources,))
        belief = self.get_prior_beliefs(data)

        for _ in range(self.num_iterations):
            trust = np.matmul(data.sc, belief)
            belief = np.matmul(data.sc.T, trust)

            # Trust and belief are normalised so that the largest entries in
            # each are 1; otherwise trust and belief scores grow without bound
            trust = trust / max(trust)
            belief = belief / max(belief)

        return Result(
            trust=list(trust),
            belief=data.get_variable_value_beliefs(belief)
        )
