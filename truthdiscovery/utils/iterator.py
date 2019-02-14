from enum import Enum

import numpy as np


class DistanceMeasures(Enum):
    """
    Enumeration of possible methods for calculating the distance between
    vectors. Note that not all methods are actually distance measures in the
    sense of metric spaces.
    """
    L1 = 1
    L2 = 2
    L_INF = 3
    COSINE = 4


class ConvergenceError(Exception):
    """
    An algorithm failed to converge within the iteration limit
    """


class Iterator:
    """
    Base class for iterators
    """
    def compare(self, _obj1, _obj2):
        """
        Log the comparison of two objects
        """
        raise NotImplementedError("Must be implemented in child classes")

    def finished(self):
        """
        Return True if iteration is finished, False otherwise
        """
        raise NotImplementedError("Must be implemented in child classes")

    def reset(self):
        """
        Rest iteration
        """
        raise NotImplementedError("Must be implemented in child classes")


class FixedIterator(Iterator):
    """
    Iterator that runs a fixed number of times, then finishes
    """
    limit = 20
    it_count = None

    def __init__(self, limit=None):
        if limit is not None:
            if limit < 0:
                raise ValueError("Iteration limit cannot be negative")
            self.limit = limit
        self.reset()

    def reset(self):
        self.it_count = 0

    def compare(self, _obj1, _obj2):
        """
        Increase the iteration count. Objects passed in are unused
        """
        self.it_count += 1

    def finished(self):
        return self.it_count >= self.limit


class ConvergenceIterator(Iterator):
    """
    Iterator that runs until the distance between vectors of interest is
    smaller than a set threshold
    """
    threshold = 0.0001
    it_count = None
    distance_measure = None
    current_distance = None
    limit = 1000000
    debug = False

    def __init__(self, distance_measure, threshold, limit=None, debug=False):
        """
        :param distance_measure: value from DistanceMeasures enumeration
        :param threshold:        iteration is finished when distance goes below
                                 this threshold value
        :param limit:            maximum number of iterations to perform
        :param debug:            if True, print out current distance at each
                                 iteration
        """
        self.it_count = 0
        self.distance_measure = distance_measure
        if threshold is not None:
            self.threshold = threshold
        if limit is not None:
            self.limit = limit
        self.debug = debug
        self.reset()

    def reset(self):
        self.it_count = 0
        self.current_distance = None

    def compare(self, obj1, obj2):
        """
        Update the most recent distance between objects
        """
        self.it_count += 1
        self.current_distance = self.get_distance(
            self.distance_measure, obj1, obj2
        )
        if self.debug:  # pragma: no cover
            print("{},{}".format(self.it_count, self.current_distance))

    def finished(self):
        """
        :raises ConvergenceError: if maximum iteration limit has been reached
                                  without distance going below threshold
        """
        if (self.current_distance is not None
                and self.current_distance < self.threshold):
            return True
        if self.it_count >= self.limit:
            raise ConvergenceError(
                "Distance did not go beneath threshold in {} iterations"
                .format(self.limit)
            )
        return False

    @classmethod
    def get_distance(cls, distance_measure, obj1, obj2):
        """
        Calculate distance between vectors using the given measure
        :param distance_measure: value from DistanceMeasures enumeration
        :param obj1:             first object to be compared
        :param obj2:             second object to be compared
        :raises ValueError: if distance_measure is not an item from the
                            DistanceMeasures enumeration
        """
        if distance_measure == DistanceMeasures.L1:
            return np.linalg.norm(obj1 - obj2, ord=1)
        if distance_measure == DistanceMeasures.L2:
            return np.linalg.norm(obj1 - obj2)
        if distance_measure == DistanceMeasures.L_INF:
            return np.linalg.norm(obj1 - obj2, ord=np.inf)
        if distance_measure == DistanceMeasures.COSINE:
            norm1 = np.linalg.norm(obj1)
            norm2 = np.linalg.norm(obj2)
            return 1 - (np.dot(obj1, obj2) / (norm1 * norm2))
        raise ValueError(
            "Invalid distance measure: '{}'".format(distance_measure)
        )
