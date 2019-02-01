class BaseAlgorithm:
    """
    Base class for truth discovery algorithms
    """
    def run(self, data):
        """
        Run the algorithm on the given data
        """
        raise NotImplementedError("Must be implemented in child classes")
