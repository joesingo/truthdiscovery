from enum import Enum

import numpy as np

from truthdiscovery.output import Result
from truthdiscovery.utils.iterator import FixedIterator


class PriorBelief(Enum):
    """
    Enumeration of possible choices for prior beliefs, used in iterative
    algorithms
    """
    FIXED = 1
    VOTED = 2
    UNIFORM = 3


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
    iterator = None
    priors = PriorBelief.FIXED

    def __init__(self, iterator=None, priors=None):
        """
        :param iterator: Iterator object to control when iteration stops
                         (optional)
        :param priors:   value from `PriorBelief` enumeration to specify which
                         prior belief values are used (optional)
        """
        self.iterator = iterator or self.get_default_iterator()
        if priors is not None:
            self.priors = priors

    def get_default_iterator(self):
        """
        Return the Iterator object to use by default, if the user does not
        provide one
        :return: an Iterator object
        """
        return FixedIterator(20)

    def get_prior_beliefs(self, data):
        """
        :param data:        input data as a Dataset object
        :return:            a numpy array of prior belief values for claims
        :raises ValueError: if self.prior is not an item from the `PriorBelief`
                            enumeration
        """
        if self.priors == PriorBelief.FIXED:
            return np.full((data.num_claims,), 0.5)

        if self.priors == PriorBelief.VOTED:
            source_counts = np.matmul(data.sc.T, np.ones((data.num_sources,)))
            return source_counts / np.matmul(data.mut_ex, source_counts)

        if self.priors == PriorBelief.UNIFORM:
            return 1 / np.matmul(data.mut_ex, np.ones((data.num_claims,)))

        raise ValueError(
            "Invalid prior belief type: '{}'".format(self.priors)
        )

    def run(self, data):
        """
        Run the algorithm on a dataset
        :param data: input data as a Dataset object
        :return: the results as a Results tuple
        """
        self.iterator.reset()
        trust, claim_belief = self._run(data)
        return Result(
            trust=list(trust),
            belief=data.get_variable_value_beliefs(claim_belief)
        )

    def _run(self, data):
        """
        Internal method for running the algorithm, to avoid including
        boilerplate code in each subclass
        :param data: Dataset object
        :return: a tuple (trust, claim_belief), where trust is a numpy array of
                 source trusts, and belief is a numpy array of claim beliefs,
                 both ordered as in the input data
        """
        raise NotImplementedError("Must be implemented in child classes")
