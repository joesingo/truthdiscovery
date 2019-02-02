import numpy as np

from truthdiscovery.algorithm.base import BaseAlgorithm
from truthdiscovery.input import SourceClaimMatrix
from truthdiscovery.output import Result


class Sums(BaseAlgorithm):
    def __init__(self, num_iterations):
        self.num_iterations = num_iterations

    def run(self, data):
        """
        :param data: input data as a SourceVariableMatrix
        """
        # Convert variables matrix to claims
        sc_mat = SourceClaimMatrix(data)

        trust = np.zeros((sc_mat.num_sources(),))
        # TODO: allow different priors to be used
        belief = np.full((sc_mat.num_claims(),), 0.5)

        for _ in range(self.num_iterations):
            trust = np.matmul(sc_mat.mat, belief)
            belief = np.matmul(sc_mat.mat.T, trust)

            # Trust and belief are normalised so that the largest entries in
            # each are 1; otherwise trust and belief scores grow without bound
            trust = trust / max(trust)
            belief = belief / max(belief)

        # Convert belief in claims to belief for each variable taking its
        # claimed values
        var_belief = [None] * data.num_variables()
        for claim, belief_score in enumerate(belief):
            var, val = sc_mat.get_claim(claim)
            if var_belief[var] is None:
                var_belief[var] = {}
            var_belief[var][val] = belief_score

        return Result(trust=list(trust), belief=var_belief)
