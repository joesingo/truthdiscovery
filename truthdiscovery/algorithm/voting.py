import time

import numpy as np

from truthdiscovery.algorithm.base import BaseAlgorithm
from truthdiscovery.output import Result


class MajorityVoting(BaseAlgorithm):
    """
    Baseline truth-discovery method, where the belief that X takes value v is
    simply the number of sources who makes that assertion. Sources are
    considered to be equally trustworthy.
    """
    def run(self, data):
        """
        :param data: input data as a :any:`Dataset` object
        :return: results as a :any:`Result` object
        """
        start_time = time.time()
        claim_belief = data.sc.T @ np.ones((data.num_sources),)
        normalised_belief = claim_belief / np.max(claim_belief)
        end_time = time.time()
        return Result(
            trust=data.get_source_trust_dict([1] * data.num_sources),
            belief=data.get_belief_dict(normalised_belief),
            time_taken=end_time - start_time
        )
