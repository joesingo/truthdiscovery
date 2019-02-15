import json
import math
from os import path

import numpy as np
import numpy.ma as ma
import pytest

from truthdiscovery.algorithm import (
    AverageLog,
    BaseAlgorithm,
    BaseIterativeAlgorithm,
    Investment,
    MajorityVoting,
    PooledInvestment,
    PriorBelief,
    Sums,
    TruthFinder
)
from truthdiscovery.input import ClaimImplicationDataset, Dataset
from truthdiscovery.utils import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator
)


class BaseTest:
    @pytest.fixture
    def data(self):
        return Dataset(ma.masked_values([
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
    def test_run_fail(self, data):
        alg = BaseIterativeAlgorithm()
        with pytest.raises(NotImplementedError):
            alg.run(data)

    def test_fixed_priors(self, data):
        alg = BaseIterativeAlgorithm(priors=PriorBelief.FIXED)
        got = alg.get_prior_beliefs(data)
        expected = [0.5, 0.5, 0.5, 0.5]
        assert np.array_equal(got, expected)

    def test_voted_priors(self, data):
        alg = BaseIterativeAlgorithm(priors=PriorBelief.VOTED)
        got = alg.get_prior_beliefs(data)
        expected = [1, 0.5, 0.5, 1]
        assert np.array_equal(got, expected)

        # Add a new value so that priors are different to voted...
        mat2 = data.sv.copy()
        mat2[2, 1] = 8
        data2 = Dataset(mat2)
        got2 = alg.get_prior_beliefs(data2)
        expected2 = [1, 1 / 3, 2 / 3, 1]
        assert np.array_equal(got2, expected2)

    def test_uniform_priors(self, data):
        alg = BaseIterativeAlgorithm(priors=PriorBelief.UNIFORM)
        got = alg.get_prior_beliefs(data)
        expected = [1, 0.5, 0.5, 1]
        assert np.array_equal(got, expected)

        # Same secondary test as for voted, but beliefs should not change here
        mat2 = data.sv.copy()
        mat2[2, 1] = 8
        data2 = Dataset(mat2)
        got2 = alg.get_prior_beliefs(data2)
        expected2 = [1, 0.5, 0.5, 1]
        assert np.array_equal(got2, expected2)

    def test_invalid_priors(self, data):
        alg = BaseIterativeAlgorithm(priors="hello")
        with pytest.raises(ValueError):
            alg.get_prior_beliefs(data)


class TestSums(BaseTest):
    def test_basic(self, data):
        """
        Perform Sums on a small graph. The expected results were obtained by
        finding eigenvectors of suitable matrices (using numpy "by hand"), as
        per Kleinberg paper for Hubs and Authorities
        """
        sums = Sums(iterator=ConvergenceIterator(DistanceMeasures.L1, 0.00001))
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
        avlog = AverageLog(iterator=FixedIterator(num_iterations))
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
        rows, cols = data.sv.shape
        new_shape = (rows + 1, cols)
        new_mat = ma.zeros(new_shape)
        new_mat[0:rows, :] = data.sv
        new_mat[rows, :] = ma.masked
        new_data = Dataset(new_mat)

        avlog = AverageLog()
        with pytest.raises(ValueError):
            avlog.run(new_data)


class TestInvestment(BaseTest):
    def test_basic(self):
        data = Dataset(ma.masked_values([
            [1, 0, 9],
            [0, 9, 0],
            [1, 1, 1],
            [9, 1, 9]
        ], 9))

        # TODO: find example that converges nicely: this one results in all
        # sources bar one having trust 0, which causes division by zero error
        num_iterations = 20
        g = 1.4
        inv = Investment(iterator=FixedIterator(num_iterations), g=g)
        results = inv.run(data)

        b = [
            2 / 3,
            1 / 3,
            2 / 3,
            1 / 3,
            1 / 2,
            1 / 2
        ]
        t = [1, 1, 1, 1]
        old_t = t[:]

        for _ in range(num_iterations):
            t[0] = (old_t[0] / 2) * (
                b[0] / ((old_t[0] / 2) + (old_t[2] / 3)) +
                b[3] / (old_t[0] / 2)
            )
            t[1] = (old_t[1] / 2) * (
                b[1] / (old_t[1] / 2) +
                b[5] / (old_t[1] / 2)
            )
            t[2] = (old_t[2] / 3) * (
                b[0] / ((old_t[0] / 2) + (old_t[2] / 3)) +
                b[2] / ((old_t[2] / 3) + old_t[3]) +
                b[4] / (old_t[2] / 3)
            )
            t[3] = old_t[3] * (
                b[2] / ((old_t[2] / 3) + old_t[3])
            )

            b[0] = ((t[0] / 2) + (t[2] / 3)) ** g
            b[1] = (t[1] / 2) ** g
            b[2] = ((t[2] / 3) + t[3]) ** g
            b[3] = (t[0] / 2) ** g
            b[4] = (t[2] / 3) ** g
            b[5] = (t[1] / 2) ** g

            max_t = max(t)
            for i, val in enumerate(t):
                t[i] = val / max_t
            old_t = t[:]

            max_b = max(b)
            for j, val in enumerate(b):
                b[j] = val / max_b

        assert np.allclose(results.trust, t)

        assert set(results.belief[0].keys()) == {0, 1}
        assert set(results.belief[1].keys()) == {0, 1}
        assert set(results.belief[2].keys()) == {0, 1}

        assert np.isclose(results.belief[0][1], b[0])
        assert np.isclose(results.belief[0][0], b[1])
        assert np.isclose(results.belief[1][1], b[2])
        assert np.isclose(results.belief[1][0], b[3])
        assert np.isclose(results.belief[2][1], b[4])
        assert np.isclose(results.belief[2][0], b[5])


class TestPooledInvestment(BaseTest):
    def test_basic(self):
        # Same data as Investment above
        data = Dataset(ma.masked_values([
            [1, 0, 9],
            [0, 9, 0],
            [1, 1, 1],
            [9, 1, 9]
        ], 9))

        num_iterations = 5
        g = 1.4
        pooled_inv = PooledInvestment(
            iterator=FixedIterator(num_iterations), g=g
        )
        results = pooled_inv.run(data)

        b = [0.5] * 6
        t = [1, 1, 1, 1]
        old_t = t[:]

        for _ in range(num_iterations):
            # Note: trust update is the same as for investment
            t[0] = (old_t[0] / 2) * (
                b[0] / ((old_t[0] / 2) + (old_t[2] / 3)) +
                b[3] / (old_t[0] / 2)
            )
            t[1] = (old_t[1] / 2) * (
                b[1] / (old_t[1] / 2) +
                b[5] / (old_t[1] / 2)
            )
            t[2] = (old_t[2] / 3) * (
                b[0] / ((old_t[0] / 2) + (old_t[2] / 3)) +
                b[2] / ((old_t[2] / 3) + old_t[3]) +
                b[4] / (old_t[2] / 3)
            )
            t[3] = old_t[3] * (
                b[2] / ((old_t[2] / 3) + old_t[3])
            )

            h = [
                (t[0] / 2) + (t[2] / 3),
                t[1] / 2,
                (t[2] / 3) + t[3],
                t[0] / 2,
                t[2] / 3,
                t[1] / 2,
            ]
            g_h = [x ** g for x in h]

            b[0] = h[0] * g_h[0] / (g_h[0] + g_h[1])
            b[1] = h[1] * g_h[1] / (g_h[0] + g_h[1])
            b[2] = h[2] * g_h[2] / (g_h[2] + g_h[3])
            b[3] = h[3] * g_h[3] / (g_h[2] + g_h[3])
            b[4] = h[4] * g_h[4] / (g_h[4] + g_h[5])
            b[5] = h[5] * g_h[5] / (g_h[4] + g_h[5])

            max_t = max(t)
            for i, val in enumerate(t):
                t[i] = val / max_t
            old_t = t[:]

            max_b = max(b)
            for j, val in enumerate(b):
                b[j] = val / max_b

        assert np.allclose(results.trust, t)

        assert set(results.belief[0].keys()) == {0, 1}
        assert set(results.belief[1].keys()) == {0, 1}
        assert set(results.belief[2].keys()) == {0, 1}

        assert np.isclose(results.belief[0][1], b[0])
        assert np.isclose(results.belief[0][0], b[1])
        assert np.isclose(results.belief[1][1], b[2])
        assert np.isclose(results.belief[1][0], b[3])
        assert np.isclose(results.belief[2][1], b[4])
        assert np.isclose(results.belief[2][0], b[5])


class TestTruthFinder(BaseTest):
    """
    Test the TruthFinder algorithm
    """
    def test_basic(self, data):
        def imp_func(var, val1, val2):
            # Make sure implication is asymmetric
            diff = val1 - val2
            if diff > 0:
                return np.exp(-0.5 * diff * diff)
            return 0.4

        imp_data = ClaimImplicationDataset(data.sv, imp_func)
        n = 50
        t_0 = 0.4
        gamma = 0.5
        ro = 0.25

        trust = [t_0, t_0, t_0]
        belief = [0] * 4

        for _ in range(n):
            tau = [
                -np.log(1 - trust[0]),
                -np.log(1 - trust[1]),
                -np.log(1 - trust[2])
            ]
            sigma = [
                tau[0] + tau[1],
                tau[0],
                tau[1],
                tau[0] + tau[2]
            ]
            sigma_star = [
                sigma[0],
                sigma[1] + ro * sigma[2] * 0.4,
                sigma[2] + ro * sigma[1] * np.exp(-0.5),
                sigma[3]
            ]
            belief = [
                1 / (1 + np.exp(-gamma * sigma_star[0])),
                1 / (1 + np.exp(-gamma * sigma_star[1])),
                1 / (1 + np.exp(-gamma * sigma_star[2])),
                1 / (1 + np.exp(-gamma * sigma_star[3]))
            ]
            trust = [
                (belief[0] + belief[1] + belief[3]) / 3,
                (belief[0] + belief[2]) / 2,
                belief[3]
            ]

        truthfinder = TruthFinder(
            dampening_factor=gamma, influence_param=ro, initial_trust=t_0,
            iterator=FixedIterator(n)
        )
        results = truthfinder.run(imp_data)

        assert np.allclose(results.trust, trust)

        assert set(results.belief[0].keys()) == {1}
        assert set(results.belief[1].keys()) == {9, 8}
        assert set(results.belief[2].keys()) == {7}

        assert np.isclose(results.belief[0][1], belief[0])
        assert np.isclose(results.belief[1][9], belief[1])
        assert np.isclose(results.belief[1][8], belief[2])
        assert np.isclose(results.belief[2][7], belief[3])

    def test_no_implications(self, data):
        """
        Perform the same run as above, but do not bother with implications
        between claims. This is to check that implications are ignored if a
        normal Dataset object is passed in, instead of ClaimImplicationDataset
        """
        n = 50
        t_0 = 0.4
        gamma = 0.5

        trust = [t_0, t_0, t_0]
        belief = [0] * 4

        for _ in range(n):
            tau = [
                -np.log(1 - trust[0]),
                -np.log(1 - trust[1]),
                -np.log(1 - trust[2])
            ]
            sigma = [
                tau[0] + tau[1],
                tau[0],
                tau[1],
                tau[0] + tau[2]
            ]
            belief = [
                1 / (1 + np.exp(-gamma * sigma[0])),
                1 / (1 + np.exp(-gamma * sigma[1])),
                1 / (1 + np.exp(-gamma * sigma[2])),
                1 / (1 + np.exp(-gamma * sigma[3]))
            ]
            trust = [
                (belief[0] + belief[1] + belief[3]) / 3,
                (belief[0] + belief[2]) / 2,
                belief[3]
            ]

        truthfinder = TruthFinder(
            dampening_factor=gamma, initial_trust=t_0,
            iterator=FixedIterator(n)
        )
        results = truthfinder.run(data)

        assert np.allclose(results.trust, trust)

        assert set(results.belief[0].keys()) == {1}
        assert set(results.belief[1].keys()) == {9, 8}
        assert set(results.belief[2].keys()) == {7}

        assert np.isclose(results.belief[0][1], belief[0])
        assert np.isclose(results.belief[1][9], belief[1])
        assert np.isclose(results.belief[1][8], belief[2])
        assert np.isclose(results.belief[2][7], belief[3])


class TestOnLargeData:
    """
    The following are regression tests, to check that the output of each
    algorithm on a (synthetic) dataset remains the same over time
    """
    @pytest.fixture
    def data(self):
        return Dataset.from_csv(self.get_filepath("data.csv"))

    def get_filepath(self, name):
        here = path.abspath(path.dirname(__file__))
        return path.join(here, "regression", name)

    def check_results(self, alg, data, exp_results_filename):
        """
        Helper method to check results of an algorithm
        :param alg: algorithm instance
        :param data: Dataset instance
        :param exp_results_filename: filename of JSON file containing expected
                                     results (name should be relative to
                                     'truthdiscovery/test/regression' in the
                                     repo)
        """
        res = alg.run(data)
        with open(self.get_filepath(exp_results_filename)) as res_file:
            exp_res = json.load(res_file)

        trust_err = "Incorrect trust for {}".format(exp_results_filename)
        assert res.trust == exp_res["trust"], trust_err

        # JSON cannot have floats as keys, so we need to convert them before
        # comparison with real results
        exp_belief = [
            {float(k): v for k, v in belief_dict.items()}
            for belief_dict in exp_res["belief"]
        ]
        belief_err = "Incorrect belief for {}".format(exp_results_filename)
        assert res.belief == exp_belief, belief_err

    def test_sums(self, data):
        sums = Sums(iterator=FixedIterator(20))
        self.check_results(sums, data, "sums_results.json")

    def test_average_log(self, data):
        average_log = AverageLog(iterator=FixedIterator(20))
        self.check_results(average_log, data, "average_log_results.json")

    def test_investment(self, data):
        investment = Investment(iterator=FixedIterator(20))
        self.check_results(investment, data, "investment_results.json")

    def test_pooled_investment(self, data):
        pooled_investment = PooledInvestment(iterator=FixedIterator(10))
        self.check_results(
            pooled_investment, data, "pooled_investment_results.json"
        )

    def test_truthfinder(self, data):
        it = ConvergenceIterator(DistanceMeasures.COSINE, 0.001)
        truthfinder = TruthFinder(iterator=it)

        def imp(var, val1, val2):
            diff = val1 - val2
            return np.exp(-0.5 * diff ** 2)

        data_with_imp = ClaimImplicationDataset(data.sv, imp)
        self.check_results(
            truthfinder, data_with_imp, "truthfinder_results.json"
        )

    def test_voting(self, data):
        voting = MajorityVoting()
        self.check_results(voting, data, "voting_results.json")


class TestIteratorsForAlgorithms:
    def test_default_iterator_types(self):
        test_data = {
            FixedIterator: (Sums, AverageLog, Investment, PooledInvestment),
            ConvergenceIterator: (TruthFinder,)
        }
        for it_cls, alg_classes in test_data.items():
            for alg_cls in alg_classes:
                obj = alg_cls()
                err_msg = ("Wrong iterator type for {}: {} instead of {}"
                           .format(alg_cls.__name__,
                                   obj.iterator.__class__.__name__,
                                   it_cls.__name__))
                assert isinstance(obj.iterator, it_cls), err_msg
