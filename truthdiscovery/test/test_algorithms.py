from truthdiscovery.algorithm import Sums
from truthdiscovery.input import SourceVariableMatrix

import numpy.ma as ma


class TestSums:
    def test_basic(self):
        data = SourceVariableMatrix(ma.masked_values([
            [1, 9,  7],
            [1, 10, 0],
            [0, 0,  7]
        ], 0))
        sums = Sums(20)
        sums.run(data)
        # assert False
