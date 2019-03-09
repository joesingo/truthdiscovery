from enum import Enum
import time

import numpy as np

from truthdiscovery.output import Result
from truthdiscovery.utils.iterator import FixedIterator


class PriorBelief(Enum):
    """
    Enumeration of possible choices for prior beliefs, used in iterative
    algorithms

    TODO: need to write a brief explanation of each choice
    """
    FIXED = "fixed"
    VOTED = "voted"
    UNIFORM = "uniform"


class BaseAlgorithm:
    """
    Base class for truth discovery algorithms
    """
    def run(self, data):
        """
        Run the algorithm on the given data

        :param data: input data as a :any:`Dataset` object
        :return: the results as a :any:`Result` tuple
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
        :param iterator: :any:`Iterator` object to control when iteration stops
                         (optional)
        :param priors:   value from :any:`PriorBelief` enumeration to specify
                         which prior belief values are used (optional)
        """
        self.iterator = iterator or self.get_default_iterator()
        if priors is not None:
            self.priors = priors

    def get_default_iterator(self):
        """
        Return the :any:`Iterator` object to use by default, if the user does
        not provide one

        :return: an :any:`Iterator` object
        """
        return FixedIterator(20)

    def get_prior_beliefs(self, data):
        """
        :param data:        input data as a :any:`Dataset` object
        :return:            a numpy array of prior belief values for claims, in
                            claim ID order
        :raises ValueError: if ``self.prior`` is not an item from the
                            :any:`PriorBelief` enumeration
        """
        if self.priors == PriorBelief.FIXED:
            return np.full((data.num_claims,), 0.5)

        if self.priors == PriorBelief.VOTED:
            source_counts = data.sc.T @ np.ones((data.num_sources,))
            return source_counts / (data.mut_ex @ source_counts)

        if self.priors == PriorBelief.UNIFORM:
            return 1 / (data.mut_ex @ np.ones((data.num_claims,)))

        raise ValueError(
            "Invalid prior belief type: '{}'".format(self.priors)
        )

    def run(self, data):
        self.iterator.reset()
        start_time = time.time()
        trust, claim_belief = self._run(data)
        end_time = time.time()
        return Result(
            trust=data.get_source_trust_dict(trust),
            belief=data.get_belief_dict(claim_belief),
            time_taken=end_time - start_time,
            iterations=self.iterator.it_count
        )

    def _run(self, data):
        """
        Internal method for running the algorithm, to avoid including
        boilerplate code in each subclass

        :param data: :any:`Dataset` object
        :return: a tuple ``(trust, claim_belief)``, where ``trust`` is a numpy
                 array of source trusts, and ``belief`` is a numpy array of
                 claim beliefs, both ordered as in the input data
        """
        raise NotImplementedError("Must be implemented in child classes")
