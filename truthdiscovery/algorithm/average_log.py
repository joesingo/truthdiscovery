import numpy as np

from truthdiscovery.algorithm.base import BaseIterativeAlgorithm
from truthdiscovery.input import SourceClaimMatrix
from truthdiscovery.output import Result


class AverageLog(BaseIterativeAlgorithm):
    """
    AverageLog by Pasternack and Roth.

    Similar to Sums (and uses the same belief update step), but updates source
    trust as average claim belief weighted by log(number of claims).
    """
    def run(self, data):
        """
        :param data: input data as a SourceVariableMatrix
        :return: the results as a Results tuple
        """
        sc_mat = SourceClaimMatrix(data)

        trust = np.zeros((data.num_sources(),))
        belief = self.get_prior_beliefs(sc_mat)

        # Pre-compute the number of claims made by each source and log
        # weighting, since this is used in each iteration and does not change.
        # Note that the number of claims made by s_i is the sum of the i-th row
        # of the claims matrix, so we multiply by [1 ... 1].T to get the counts
        # for all sources in one operation
        claim_counts = np.matmul(sc_mat.mat, np.ones((sc_mat.num_claims(),)))

        # TODO: decide how to handle this case better
        if np.any(claim_counts == 0):
            raise ValueError("All sources must make at least one claim")

        weights = np.log(claim_counts) / claim_counts

        for _ in range(self.num_iterations):
            # Entry-wise multiplication
            trust = weights * np.matmul(sc_mat.mat, belief)
            belief = np.matmul(sc_mat.mat.T, trust)

            # Normalise as with sums
            trust = trust / max(trust)
            belief = belief / max(belief)

        return Result(
            trust=list(trust),
            belief=self.get_variable_beliefs(data, sc_mat, belief)
        )
