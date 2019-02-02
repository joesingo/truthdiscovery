import numpy as np


class SourceVariableMatrix:
    """
    A matrix containing data about variables and the values they take according
    to different sources.

    Columns correspond to variables, and rows correspond to sources. Let
    X_1, ..., X_n be the variables, and s_1, ... s_m be the sources. A value v
    at entry (i, j) means that s_i asserts that X_j = v

    No entry at (i, j) means that s_i does not make any assertions regarding
    the value of X_j
    """

    def __init__(self, matrix):
        """
        :param matrix: 2D numpy array giving entries of the matrix. May be a
                       masked array to encode missing values, i.e. where a
                       sources makes no claims as to the value of a variable.
        raises ValueError: if the dimension of the input is invalid
        """
        self.mat = matrix
        if self.mat.ndim != 2:
            raise ValueError("Source/variables matrix must be two dimensional")

    def num_sources(self):
        """
        :return: the number of sources
        """
        return self.mat.shape[0]

    def num_variables(self):
        """
        :return: the number of variables
        """
        return self.mat.shape[1]

    @classmethod
    def from_csv(cls, path):
        """
        Load a matrix from a CSV file
        """
        return cls(np.genfromtxt(path, delimiter=",", usemask=True))
