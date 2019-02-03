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
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        raise NotImplementedError("Must be implemented in child classes")


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
        :param data: input data as a Dataset object
        :return:     a numpy array of prior belief values for claims
        :raises ValueError: if self.prior is not an item from the `PriorBelief`
                            enumeration
        """
        num_claims = data.num_claims
        if self.priors == PriorBelief.FIXED:
            return np.full((num_claims,), 0.5)

        raise ValueError(
            "Invalid prior belief type: '{}'".format(self.priors)
        )
