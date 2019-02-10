import numpy as np

from truthdiscovery.input.dataset import Dataset


class ClaimImplicationDataset(Dataset):
    """
    A dataset that may include implication values between claims (e.g. for
    TruthFinder)

    The implication between claims `var = x` and `var = y` is a value in
    [-1, 1] that describes how the confidence that var = x influces the
    confidence of var = y.

    A positive value indicates that if var = x is true, then var = y is likely
    to be true. A negative value means that if var = x is true, then var = y is
    likely to be false (Yin et.  al., 2008).
    """
    def __init__(self, sv_mat, implication_function):
        """
        :param sv_mat:               source-variables matrix as for Dataset
                                     constructor
        :param implication_function: callback function to compute implication
                                     values. Should take (var, val1, val2) as
                                     arguments, and return
                                     imp(var=val1 -> var=val2), or None
        """
        super().__init__(sv_mat)
        self.imp = np.zeros((self.num_claims, self.num_claims))
        for j1, j2 in np.argwhere(self.mut_ex == 1):
            var, val1 = self.claims[j1]
            val2 = self.claims[j2].val
            # Note that claims j1 and j2 are for the same variable, since mut
            # ex is 1 at this point
            imp_value = implication_function(var, val1, val2)
            if imp_value is not None:
                if imp_value < -1 or imp_value > 1:
                    raise ValueError("Implication values must be in [-1, 1]")
                self.imp[j1, j2] = imp_value
