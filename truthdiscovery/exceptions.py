class ConvergenceError(Exception):
    """
    An algorithm failed to converge within the iteration limit
    """


class EarlyFinishError(Exception):
    """
    Error raised when an iterative algorithm is forced to finish early, e.g.
    due to rounding errors preventing further computations
    """


class EmptyDatasetError(Exception):
    """
    An algorithm was run on a dataset containing no claims
    """
