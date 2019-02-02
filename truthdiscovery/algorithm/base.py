from enum import Enum

import numpy as np


class PriorBelief(Enum):
    """
    Enumeration of possible choices for prior beliefs, used in iterative
    algorithms
    """
    FIXED = 1


class BaseAlgorithm:
    """
    Base class for truth discovery algorithms
    """
    def run(self, data):
        """
        Run the algorithm on the given data
        :param data: input data as a SourceVariableMatrix
        :return: the results as a Results tuple
        """
        raise NotImplementedError("Must be implemented in child classes")

    @staticmethod
    def get_variable_beliefs(sv_matrix, sc_matrix, belief):
        """
        Convert belief in claims to belief for each variable taking its claimed
        values
        :param sv_matrix: original data as a SourceVariableMatrix
        :param sc_matrix: SourceClaimMatrix generated from `sv_matrix`, from
                          which `belief` has been generated
        :param belief:    numpy array of belief values for claims in
                          `sc_matrix`
        :return: a list of belief values for variables taking different values,
                 in the format required for `Result`
        """
        var_belief = [None] * sv_matrix.num_variables()
        for claim, belief_score in enumerate(belief):
            var, val = sc_matrix.get_claim(claim)
            if var_belief[var] is None:
                var_belief[var] = {}
            var_belief[var][val] = belief_score
        return var_belief


class BaseIterativeAlgorithm(BaseAlgorithm):
    """
    Base class for functionality common to algorithms that iteratively compute
    trust and belief
    """
    num_iterations = 20
    priors = PriorBelief.FIXED

    def __init__(self, num_iterations=None, priors=None):
        """
        :param num_iterations: the number of iterations to perform
        :param priors:         value from `PriorBelief` enumeration to specify
                               which prior belief values are used
        """
        if num_iterations is not None:
            self.num_iterations = num_iterations

        if priors is not None:
            self.priors = priors

    def get_prior_beliefs(self, data):
        """
        :param data: input data as a SourceClaimMatrix
        :return:     a numpy array of prior belief values for claims
        :raises ValueError: if self.prior is not an item from the `PriorBelief`
                            enumeration
        """
        num_claims = data.num_claims()
        if self.priors == PriorBelief.FIXED:
            return np.full((num_claims,), 0.5)

        raise ValueError(
            "Invalid prior belief type: '{}'".format(self.priors)
        )
