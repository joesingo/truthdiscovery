import os

import numpy as np
import numpy.ma as ma

from truthdiscovery.input.dataset import Dataset


def csv_to_masked_array(fileobj):
    """
    Parse a CSV file and return a numpy masked array

    :param fileobj:     fileobj to read from
    :return:            a numpy masked array representing the matrix encoded by
                        the CSV
    :raises ValueError: if CSV contains values that cannot be converted to
                        floats, or if shape is invalid
    """
    entries = []
    width = None
    csv = fileobj.read().strip()
    for i, line in enumerate(csv.split(os.linesep)):
        # Split by comma and remove extra whitespace from each value
        row = list(map(str.strip, line.split(",")))
        if width is None:
            width = len(row)
        elif len(row) != width:
            raise ValueError("Expected {} entries in row {}, got {}"
                             .format(width, i + 1, len(row)))
        entries.append([float(val) if val else np.nan for val in row])

    matrix = np.array(entries)
    return ma.masked_array(matrix, np.isnan(matrix))


class MatrixDataset(Dataset):
    """
    A truth-discovery dataset given as a matrix, where columns correspond to
    variables, and rows correspond to sources.

    Let ``X_1, ..., X_n`` be the variables, and ``s_1, ... s_m`` be the
    sources. A value ``v`` at entry ``(i, j)`` means that ``s_i`` asserts that
    ``X_j = v``.

    No entry at ``(i, j)`` means that ``s_i`` does not make any assertions
    regarding the value of ``X_j``.
    """
    def __init__(self, sv_mat, *args, **kwargs):
        """
        :param sv_mat: source-variables matrix as a 2D numpy array. May be a
                       masked array to encode missing values
        :raises ValueError: if the dimension of the input is invalid
        """
        self.sv = sv_mat
        if self.sv.ndim != 2:
            raise ValueError("Source/variables matrix must be two dimensional")

        super().__init__(self.get_triples(), *args, **kwargs)

    def get_triples(self):
        """
        :yield: triples ``(source, var, val)`` for each non-empty entry in the
                matrix. Source and variable labels are defined as their row and
                column numbers respectively.
        """
        for source, row in enumerate(self.sv):
            for var, val in enumerate(row):
                if not ma.is_masked(val):
                    yield (source, var, val)

    @classmethod
    def from_csv(cls, fileobj):
        """
        Load a matrix from a CSV file

        :param fileobj:     file object to read from
        :return:            a :any:`MatrixDataset` object
        :raises ValueError: if CSV is invalid
        """
        try:
            return cls(csv_to_masked_array(fileobj))
        except ValueError as ex:
            raise ValueError("invalid matrix CSV: {}".format(ex))

    def to_csv(self):
        """
        :return: a string representation of the dataset in CSV format
        """
        return "\n".join(
            ",".join("" if ma.is_masked(val) else str(val) for val in row)
            for row in self.sv
        )
