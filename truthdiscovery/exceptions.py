class ConvergenceError(Exception):
    """
    An algorithm failed to converge within the iteration limit
    """


class RoundingError(Exception):
    """
    Error raised when an algorithm cannot perform its required calculations
    because trust/belief have been rounded
    """
