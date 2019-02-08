import random

import numpy.ma as ma

from truthdiscovery.input.dataset import Dataset


class SupervisedDataset(Dataset):
    """
    A dataset for which the true values of a subset of the variables is known
    """
    def __init__(self, sv_mat, true_values, *args, **kwargs):
        """
        :param sv_mat:      Source-variables matrix (as for Dataset
                            constructor)
        :param true_values: numpy array of true values for the variables.
                            Length must be the same as the number of variables.
                            May be a masked array if not all true values are
                            known.
        """
        super().__init__(sv_mat, *args, **kwargs)

        if true_values.ndim != 1 or true_values.shape[0] != sv_mat.shape[1]:
            raise ValueError(
                "Number of true values must be the same as the number of"
                "variables"
            )

        self.values = true_values

    def get_accuracy(self, results):
        """
        Calculate the accuracy of truth-discovery results, computed as the
        frequency of cases where the most believed value for a variable is the
        correct one.

        :param results: Results object
        :return: accuracy as a number in [0, 1]: 1 is best accuracy, 0 is worst
        """
        total = 0
        count = 0
        for var, true_value in enumerate(self.values):
            if ma.is_masked(true_value):
                continue

            # If only one value is claimed across all sources then any
            # algorithm will guess the same value (there is only one to choose
            # from), so it is not meaningful to include this variable in the
            # accuracy calculation
            if len(results.belief[var]) == 1:
                continue

            total += 1
            # Note: select value randomly if more than one most-believed value
            # exists
            most_believed = random.choice(
                list(results.get_most_believed_values(var))
            )
            if most_believed == true_value:
                count += 1
        if total == 0:
            raise ValueError(
                "No known variables where more than one claimed value exists"
            )
        return count / total

    @classmethod
    def from_csv(cls, path):
        """
        Load a matrix from a CSV file along with true values. The format is the
        same as for loading an unsupervised dataset, but the first row contains
        the true values.

        :param path: path on disk to a CSV file
        :return:     a SupervisedDataset object representing the matrix encoded
                     by the CSV
        """
        unsup = Dataset.from_csv(path)
        true_values = unsup.sv[0, :]
        sv_mat = unsup.sv[1:, :]
        return cls(sv_mat, true_values)
