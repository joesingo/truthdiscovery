import math

import numpy as np
import numpy.ma as ma
import pytest

from truthdiscovery.algorithm import (
    AverageLog, BaseAlgorithm, BaseIterativeAlgorithm, MajorityVoting, Sums,
    PriorBelief
)
from truthdiscovery.input import SourceClaimMatrix, SourceVariableMatrix


class BaseTest:
    @pytest.fixture
    def data(self):
        return SourceVariableMatrix(ma.masked_values([
            [1, 9, 7],
            [1, 8, 0],
            [0, 0, 7]
        ], 0))


class TestBase(BaseTest):
    def test_run_base_fail(self, data):
        alg = BaseAlgorithm()
        with pytest.raises(NotImplementedError):
            alg.run(data)


class TestVoting(BaseTest):
    def test_basic(self, data):
        voting = MajorityVoting()
        results = voting.run(data)
        assert results.trust == [1, 1, 1]
        assert results.belief == [
            {1: 2},
            {9: 1, 8: 1},
            {7: 2}
        ]


class TestBaseIterative(BaseTest):
    def test_fixed_priors(self, data):
        sc_mat = SourceClaimMatrix(data)
        alg = BaseIterativeAlgorithm(priors=PriorBelief.FIXED)
        got = alg.get_prior_beliefs(sc_mat)
        expected = [0.5, 0.5, 0.5, 0.5]
        assert np.array_equal(got, expected)

    def test_invalid_priors(self, data):
        sc_mat = SourceClaimMatrix(data)
        alg = BaseIterativeAlgorithm(priors="hello")
        with pytest.raises(ValueError):
            alg.get_prior_beliefs(sc_mat)


class TestSums(BaseTest):
    def test_basic(self, data):
        """
        Perform Sums on a small graph. The expected results were obtained by
        finding eigenvectors of suitable matrices (using numpy "by hand"), as
        per Kleinberg paper for Hubs and Authorities
        """
        sums = Sums(20)
        results = sums.run(data)
        assert np.allclose(results.trust, [1, 0.53208889, 0.34729636])

        assert set(results.belief[0].keys()) == {1}
        assert np.isclose(results.belief[0][1], 1)

        assert set(results.belief[1].keys()) == {9, 8}
        assert np.isclose(results.belief[1][9], 0.65270364)
        assert np.isclose(results.belief[1][8], 0.34729636)

        assert set(results.belief[2].keys()) == {7}
        assert np.isclose(results.belief[2][7], 0.87938524)


class TestAverageLog(BaseTest):
    def test_basic(self, data):
        num_iterations = 20
        avlog = AverageLog(num_iterations)
        results = avlog.run(data)

        t = [0, 0, 0]
        b = [0.5, 0.5, 0.5, 0.5]

        for _ in range(num_iterations):
            t[0] = math.log(3) * (b[0] + b[1] + b[3]) / 3
            t[1] = math.log(2) * (b[0] + b[2]) / 2
            t[2] = 0

            b[0] = t[0] + t[1]
            b[1] = t[0]
            b[2] = t[1]
            b[3] = t[0] + t[2]

            max_t = max(t)
            max_b = max(b)
            for i, val in enumerate(t):
                t[i] = val / max_t
            for j, val in enumerate(b):
                b[j] = val / max_b

        assert np.allclose(results.trust, t)

        assert set(results.belief[0].keys()) == {1}
        assert set(results.belief[1].keys()) == {9, 8}
        assert set(results.belief[2].keys()) == {7}

        assert np.isclose(results.belief[0][1], b[0])
        assert np.isclose(results.belief[1][9], b[1])
        assert np.isclose(results.belief[1][8], b[2])
        assert np.isclose(results.belief[2][7], b[3])

    def test_with_zero_rows(self, data):
        # Copy the data and add a new source who makes no claims
        rows, cols = data.mat.shape
        new_shape = (rows + 1, cols)
        new_mat = ma.zeros(new_shape)
        new_mat[0:rows, :] = data.mat
        new_mat[rows, :] = ma.masked
        new_data = SourceVariableMatrix(new_mat)

        avlog = AverageLog()
        with pytest.raises(ValueError):
            avlog.run(new_data)
