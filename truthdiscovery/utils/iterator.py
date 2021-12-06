from enum import Enum

import numpy as np

from truthdiscovery.exceptions import ConvergenceError


class DistanceMeasures(Enum):
    """
    Enumeration of possible methods for calculating the distance between
    vectors. Note that not all methods are actually distance measures in the
    sense of metric spaces.
    """
    #: L1 norm (Manhattan distance)
    L1 = "l1"
    #: L2 norm (Euclidean distance)
    L2 = "l2"
    #: Infinity norm
    L_INF = "l_inf"
    #: 1 - cosine similarity
    COSINE = "cosine"


class Iterator:
    """
    Base class for iterators
    """
    it_count = 0

    def compare(self, _obj1, _obj2):
        """
        Log the comparison of two objects
        """
        # By default just increase iteration count without comparing objects at
        # all
        self.it_count += 1

    def finished(self):
        """
        Return True if iteration is finished, False otherwise
        """
        raise NotImplementedError("Must be implemented in child classes")

    def reset(self):
        """
        Reset iteration
        """
        self.it_count = 0


class FixedIterator(Iterator):
    """
    Iterator that runs a fixed number of times, then finishes
    """
    limit = 20

    def __init__(self, limit=None):
        """
        :param limit: number of iterations to perform
        """
        if limit is not None:
            if limit < 0:
                raise ValueError("Iteration limit cannot be negative")
            self.limit = limit
        self.reset()

    def finished(self):
        return self.it_count >= self.limit


class ConvergenceIterator(Iterator):
    """
    Iterator that runs until the distance between vectors of interest is
    smaller than a set threshold
    """
    threshold = 0.0001
    distance_measure = None
    current_distance = None
    limit = 1000000
    debug = False

    def __init__(self, distance_measure, threshold, limit=None, debug=False):
        """
        :param distance_measure: value from :any:`DistanceMeasures` enumeration
        :param threshold:        iteration is finished when distance goes below
                                 this threshold value
        :param limit:            upper limit on number of iterations to perform
        :param debug:            if True, print out current distance at each
                                 iteration
        """
        self.distance_measure = distance_measure
        if threshold is not None:
            self.threshold = threshold
        if limit is not None:
            self.limit = limit
        self.debug = debug
        self.reset()

    def reset(self):
        super().reset()
        self.current_distance = None

    def compare(self, obj1, obj2):
        """
        Update the most recent distance between objects
        """
        super().compare(obj1, obj2)
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
                "Did not converge in {} iterations".format(self.limit)
            )
        return False

    @classmethod
    def get_distance(cls, distance_measure, obj1, obj2):
        """
        Calculate distance between vectors using the given measure

        :param distance_measure: value from :any:`DistanceMeasures` enumeration
        :param obj1:             first object to be compared
        :param obj2:             second object to be compared
        :raises ValueError: if ``distance_measure`` is not an item from the
                            :any:`DistanceMeasures` enumeration
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
            if norm1 == 0 or norm2 == 0:
                return 1
            return np.clip(1 - (np.dot(obj1, obj2) / (norm1 * norm2)), 0, 1)
        raise ValueError(
            "Invalid distance measure: '{}'".format(distance_measure)
        )


class OrdinalConvergenceIterator(Iterator):
    """
    Iterator that runs until the ranking associated with a vector remains
    unchanged for a specified number of iterations
    """
    threshold = 20
    current_count = 0

    def __init__(self, threshold=None):
        super().__init__()
        if threshold is not None:
            self.threshold = threshold

    def compare(self, obj1, obj2):
        super().compare(obj1, obj2)
        r1 = self.get_ranking_vector(obj1)
        r2 = self.get_ranking_vector(obj2)
        if np.all(r1 == r2):
            self.current_count += 1
            # print(f"ranking is the same; count is now {self.current_count}")
        else:
            self.current_count = 0
            # print("ranking changed")

    def finished(self):
        return self.current_count >= self.threshold

    @classmethod
    def get_ranking_vector(cls, v):
        """
        Return the ranking associated with a vector
        """
        sorted_scores = v[np.argsort(v)]
        rank = 0
        rank_mapping = {}
        for i, sc in enumerate(sorted_scores):
            if i > 0 and sc > sorted_scores[i - 1]:
                rank += 1
            rank_mapping[sc] = rank
        rv = np.zeros(v.shape)
        for i, sc in enumerate(v):
            rv[i] = rank_mapping[sc]
        return rv

    def reset(self):
        super().reset()
        self.current_count = 0
