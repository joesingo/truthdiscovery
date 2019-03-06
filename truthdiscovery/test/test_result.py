from unittest.mock import Mock, patch

import numpy as np
import pytest

from truthdiscovery.algorithm import MajorityVoting, Sums
from truthdiscovery.input import Dataset
from truthdiscovery.output import Result
from truthdiscovery.utils import FixedIterator


# Make a mocked time.time() function that returns increasing multiples of 5
MockedTime = Mock(side_effect=range(1, 100000, 5))


class TestResult:
    @pytest.fixture
    def example_results(self):
        trust = {
            "s1": 0.5,
            "s2": 0.7,
            "s3": 0.1
        }
        belief = {
            "x": {"red": 0.4, "blue": 0.9, "green": 0.5},
            "y": {"red": 0.1, "blue": 0.8, "green": 0},
            "z": {"red": 0.7, "blue": 0.7, "green": 1},
        }
        return Result(trust, belief, time_taken=0.5, iterations=100)

    def test_most_believed_values(self):
        test_data = (
            ({10: 0.5, 11: 0.7, 12: 0.7}, {11, 12}),
            ({-1: 0.1, -2: 0.1, 3: 0.05}, {-1, -2}),
            ({5: 0.9, 5000: 0.8}, {5}),
            ({123.456: 0.0001}, {123.456})
        )
        trust = [0.5] * 10
        for var_belief, exp in test_data:
            res = Result(trust, [var_belief], time_taken=None)
            assert set(res.get_most_believed_values(0)) == exp

    def test_num_iterations(self):
        data = Dataset([("source 1", "x", 7), ("source 2", "x", 8)])
        voting_res = MajorityVoting().run(data)
        assert voting_res.iterations is None

        sums_res = Sums(iterator=FixedIterator(13)).run(data)
        assert sums_res.iterations == 13

    @patch("time.time", MockedTime)
    def test_time_taken(self):
        """
        Test run time in Result objects for iterative and non-iterative
        algorithms
        """
        data = Dataset([("source 1", "x", 7), ("source 2", "x", 8)])
        res = MajorityVoting().run(data)
        assert res.time_taken == 5
        res = Sums().run(data)
        assert res.time_taken == 5

    def test_filter_result(self, example_results):
        res = example_results

        # Filter by sources
        source_filtered = res.filter(sources=("s1", "s3"))
        assert set(source_filtered.trust.keys()) == {"s1", "s3"}
        assert source_filtered.iterations == res.iterations
        assert source_filtered.time_taken == res.time_taken
        # belief should not be affected when only filtering on sources
        assert source_filtered.belief == res.belief
        # trust/belief dicts should be copies
        source_filtered.belief["x"]["red"] = 1000
        assert res.belief["x"]["red"] == 0.4

        # Filter by variables
        vars_filtered = res.filter(variables=("y", "z"))
        assert set(vars_filtered.belief.keys()) == {"y", "z"}
        assert vars_filtered.iterations == res.iterations
        assert vars_filtered.time_taken == res.time_taken
        assert vars_filtered.trust == res.trust

        # Filter both at the same time
        both_filtered = res.filter(sources=("s3", "s2"), variables=("z"))
        assert set(both_filtered.trust.keys()) == {"s2", "s3"}
        assert set(both_filtered.belief.keys()) == {"z"}

        # Shouldn't get an exception if a source/variable doesn't exist
        invalid_source = res.filter(sources=("joe", "s1"))
        invalid_var = res.filter(variables=("w", "x"))
        assert set(invalid_source.trust.keys()) == {"s1"}
        assert set(invalid_var.belief.keys()) == {"x"}

        # Edge case: filter set is empty
        empty_sources = res.filter(sources=[])
        empty_vars = res.filter(variables=[])
        assert not empty_sources.trust
        assert not empty_vars.belief
        assert empty_sources.belief == res.belief
        assert empty_vars.trust == res.trust

        # Edge case: no filtering
        no_filter = res.filter()
        assert no_filter.trust == res.trust
        assert no_filter.belief == res.belief

        # Should be able to use any iterable for filter set
        def mygen():
            yield "s1"
            yield "s3"
        gen_filter = res.filter(sources=mygen())
        assert set(gen_filter.trust.keys()) == {"s1", "s3"}

    def test_stats(self, example_results):
        res = example_results
        mean_trust, stddev_trust = res.get_trust_stats()
        assert mean_trust == (1.3 / 3)
        assert stddev_trust == 0.2494438257849294

        belief_stats = res.get_belief_stats()
        exp_x = (0.6, 0.21602468994692867)
        exp_y = (0.3, 0.3559026084010437)
        exp_z = (0.8, 0.14142135623730953)

        assert set(belief_stats.keys()) == {"x", "y", "z"}
        assert np.isclose(belief_stats["x"], exp_x).all()
        assert np.isclose(belief_stats["y"], exp_y).all()
        assert np.isclose(belief_stats["z"], exp_z).all()
