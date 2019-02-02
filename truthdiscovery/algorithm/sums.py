import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm
from truthdiscovery.input import SourceClaimMatrix
from truthdiscovery.output import Result


class Sums(BaseIterativeAlgorithm):
    """
    Sums, or Hubs and Authorities, algorithm.

    Described by Kleinberg for web pages, and adapted to truth-discovery by
    Pasternack and Roth
    """
    def run(self, data):
        """
        :param data: input data as a SourceVariableMatrix
        :return: the results as a Results tuple
        """
        # Convert variables matrix to claims
        sc_mat = SourceClaimMatrix(data)

        trust = np.zeros((sc_mat.num_sources(),))
        belief = self.get_prior_beliefs(sc_mat)

        for _ in range(self.num_iterations):
            trust = np.matmul(sc_mat.mat, belief)
            belief = np.matmul(sc_mat.mat.T, trust)

            # Trust and belief are normalised so that the largest entries in
            # each are 1; otherwise trust and belief scores grow without bound
            trust = trust / max(trust)
            belief = belief / max(belief)

        return Result(
            trust=list(trust),
            belief=self.get_variable_beliefs(data, sc_mat, belief)
        )
