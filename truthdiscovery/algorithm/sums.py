from truthdiscovery.algorithm import BaseAlgorithm
from truthdiscovery.input import SourceClaimMatrix

import numpy as np


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

        # TODO: return output
        for source, trust in enumerate(trust):
            print("source {} has trust {:.4f}".format(source, trust))

        var_beliefs = {}
        for claim, belief in enumerate(belief):
            var, val = sc_mat.get_claim(claim)
            if var not in var_beliefs:
                var_beliefs[var] = []
            var_beliefs[var].append((val, belief))

        for var, beliefs in var_beliefs.items():
            print("var {}:".format(var))
            for val, belief in beliefs:
                print(" = {}: belief {:.4f}".format(val, belief))
