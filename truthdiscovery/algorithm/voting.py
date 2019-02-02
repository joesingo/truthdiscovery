import numpy.ma as ma

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
        :param data: input data as a SourceVariableMatrix
        """
        m = data.mat
        var_belief = []
        for col in m.T:
            beliefs = {}
            for val in col:
                if ma.is_masked(val):
                    continue
                if val not in beliefs:
                    beliefs[val] = 0
                beliefs[val] += 1
            var_belief.append(beliefs)

        return Result(trust=[1] * data.num_sources(), belief=var_belief)
