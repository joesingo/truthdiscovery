import pytest

import numpy as np

from truthdiscovery.utils import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator,
    Iterator
)


class TestBaseIterator:
    def test_run_base_fail(self):
        it = Iterator()
        with pytest.raises(NotImplementedError):
            it.compare(1, 2)
        with pytest.raises(NotImplementedError):
            it.finished()


class TestFixedIterator:
    def test_invalid_limit(self):
        invalid = (-1, -2)
        for limit in invalid:
            with pytest.raises(ValueError):
                FixedIterator(limit)

    def test_finish_condition(self):
        limit = 24
        it = FixedIterator(limit)
        it_count = 0
        # Careful: if implementation is completely broken the following may be
        # an infinite loop
        while not it.finished():
            # Do some stuf...
            it_count += 1
            # Objects compared here should not matter
            it.compare("hello", {"blah": 999})
        assert it_count == limit

    def test_reset(self):
        limit = 24
        it = FixedIterator(limit)
        # Run the iterator down
        while not it.finished():
            it.compare(1, 2)
        # Reset: should no longer be finished
        it.reset()
        assert not it.finished()
        # Check can run it down again
        it_count = 0
        while not it.finished():
            it_count += 1
            it.compare(1, 2)
        assert it_count == limit


class TestConvergenceIterator:
    def test_basic(self):
        threshold = 0.51
        it_count = 0
        it = ConvergenceIterator(DistanceMeasures.L1, threshold)
        current_distance = 1
        while not it.finished():
            it_count += 1
            current_distance -= 0.02
            it.compare(np.array([1]), np.array([1 + current_distance]))
        assert it_count == 25

    def test_invalid_distance_measures(self):
        invalid = ("L1", 1, 2, None)
        obj1 = np.array([1, 0.5, 0.4])
        obj2 = np.array([0.9, 0.8, 0.7])
        for measure in invalid:
            with pytest.raises(ValueError):
                ConvergenceIterator.get_distance(measure, obj1, obj2)


class TestDistanceMeasures:
    def check(self, measure, obj1, obj2, exp_distance):
        got = ConvergenceIterator.get_distance(
            measure, np.array(obj1), np.array(obj2)
        )
        assert got == exp_distance

    def test_l1(self):
        self.check(DistanceMeasures.L1, [1, 2, 3, 4], [0, 3, -4, 1], 12)

    def test_l2(self):
        self.check(
            DistanceMeasures.L2,
            [1, 2, 3, 4],
            [0, 3, -4, 1],
            7.745966692414834
        )

    def test_l_inf(self):
        self.check(DistanceMeasures.L_INF, [1, 2, 3, 4], [0, 3, -4, 1], 7)

    def test_cosine(self):
        self.check(
            DistanceMeasures.COSINE,
            [0, 1, 1.5, 2],
            [1, 1, 0.3, 0.2],
            0.5292255080098709
        )
