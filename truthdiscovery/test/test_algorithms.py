import numpy.ma as ma
import pytest

from truthdiscovery.algorithm import BaseAlgorithm, Sums
from truthdiscovery.input import SourceVariableMatrix


class BaseTest:
    @pytest.fixture
    def data(self):
        return SourceVariableMatrix(ma.masked_values([
            [1, 9, 7],
            [1, 8, 0],
            [0, 0, 7]
        ], 0))


class TestSums(BaseTest):
    def test_basic(self, data):
        # TODO: actually test something here
        sums = Sums(20)
        sums.run(data)
        # assert False


class TestBase(BaseTest):
    def test_run_base_fail(self, data):
        alg = BaseAlgorithm()
        with pytest.raises(NotImplementedError):
            alg.run(data)
