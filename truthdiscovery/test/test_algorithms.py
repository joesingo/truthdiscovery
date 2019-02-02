import numpy as np
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
        """
        Perform Sums on a small graph. The expected results were obtained by
        finding eigenvectors of suitable matrices (using numpy "by hand"), as
        per Kleinberg paper for Hubs and Authorities
        """
        sums = Sums(20)
        results = sums.run(data)
        assert np.isclose(results.trust, [1, 0.53208889, 0.34729636]).all()

        assert set(results.belief[0].keys()) == {1}
        assert np.isclose(results.belief[0][1], 1)

        assert set(results.belief[1].keys()) == {9, 8}
        assert np.isclose(results.belief[1][9], 0.65270364)
        assert np.isclose(results.belief[1][8], 0.34729636)

        assert set(results.belief[2].keys()) == {7}
        assert np.isclose(results.belief[2][7], 0.87938524)


class TestBase(BaseTest):
    def test_run_base_fail(self, data):
        alg = BaseAlgorithm()
        with pytest.raises(NotImplementedError):
            alg.run(data)
