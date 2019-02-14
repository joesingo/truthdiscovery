from enum import Enum

import numpy as np


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
        """
        Rest the iteration count
        """
        self.it_count = 0

    def compare(self, _obj1, _obj2):
        """
        Increase the iteration count. Objects passed in are unused
        """
        self.it_count += 1

    def finished(self):
        """
        Return True if iteration limit has been reached, else False
        """
        return self.it_count >= self.limit


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


class ConvergenceIterator(Iterator):
    """
    Iterator that runs until the distance between vectors of interest is
    smaller than a set threshold
    """
    threshold = 0.0001
    distance_measure = None
    current_distance = None

    def __init__(self, distance_measure, threshold):
        """
        :param distance_measure: value from DistanceMeasures enumeration
        :param threshold:        iteration is finished when distance goes below
                                 this threshold value
        """
        self.distance_measure = distance_measure
        if threshold is not None:
            self.threshold = threshold

    def compare(self, obj1, obj2):
        """
        Update the most recent distance between objects
        """
        self.current_distance = self.get_distance(
            self.distance_measure, obj1, obj2
        )

    def finished(self):
        """
        Return True if the most recent distance is below the threshold, else
        False
        """
        return (self.current_distance is not None
                and self.current_distance < self.threshold)

    @classmethod
    def get_distance(self, distance_measure, obj1, obj2):
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
