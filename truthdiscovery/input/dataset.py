from collections import namedtuple
import itertools

import numpy as np
import numpy.ma as ma


#: A claim in this context is an statement of the form X=v where X is a
#: variable and v is a value. Here `var` is the index of the variable in the
#: original data, and `val` is the value.
Claim = namedtuple("Claim", ["var", "val"])


class Dataset:
    """
    An object to represent a dataset upon which truth-discovery will be
    performed. A dataset consists *variables* and the values they take
    according to different *sources*.

    The data is given as a matrix where columns correspond to variables, and
    rows correspond to sources. Let X_1, ..., X_n be the variables, and s_1,
    ... s_m be the sources. A value v at entry (i, j) means that s_i asserts
    that X_j = v.

    No entry at (i, j) means that s_i does not make any assertions regarding
    the value of X_j.
    """
    def __init__(self, sv_mat):
        """
        :param sv_mat: Source-variables matrix as a 2D numpy array. May be a
                       masked array to encode missing values
        raises ValueError: if the dimension of the input is invalid
        """
        self.sv = sv_mat
        if self.sv.ndim != 2:
            raise ValueError("Source/variables matrix must be two dimensional")

        self.num_sources, self.num_variables = self.sv.shape

        # Keep a list of the claims as Claim tuples
        self.claims = []

        # Map each Claim tuple to a list of sources that make the claim so we
        # can construct the claims matrix.
        claim_to_sources = {}

        # Keep track of a list of lists of claim indexes for claims relating to
        # the same variable: these are mutually exclusive
        mut_ex_groups = []

        for var, col in enumerate(self.sv.T):
            mut_ex_claims = []
            for source, val in enumerate(col):
                if ma.is_masked(val):
                    continue

                claim = Claim(var, val)
                if claim not in claim_to_sources:
                    # We have an unseen claim here: add it to the list
                    claim_index = len(self.claims)
                    self.claims.append(claim)
                    claim_to_sources[claim] = []
                    # This claim is mutually exclusive with the other claims
                    # seen for this variable
                    mut_ex_claims.append(claim_index)

                claim_to_sources[claim].append(source)

            mut_ex_groups.append(mut_ex_claims)

        self.num_claims = len(self.claims)

        # Create source-claim matrix: entry (i, j) is 1 if source i makes claim
        # j, and 0 otherwise
        self.sc = np.zeros((self.num_sources, self.num_claims))
        for j, claim in enumerate(self.claims):
            for source in claim_to_sources[claim]:
                self.sc[source, j] = 1

        # Create mutual exclusion matrix: entry (i, j) is 1 if claims i and j
        # relate to the same variable (including when i=j) and 0 otherwise
        self.mut_ex = np.zeros((self.num_claims, self.num_claims))
        for group in mut_ex_groups:
            for i, j in itertools.product(group, repeat=2):
                self.mut_ex[i, j] = 1

    def get_variable_value_beliefs(self, claim_beliefs):
        """
        Convert belief in claims to belief in (var, val) pairs.

        :param belief: numpy array of belief values for claims
        :return:       a list of belief values for variables taking different
                       values, in the format required for `Result`
        """
        var_beliefs = [{} for _ in range(self.num_variables)]
        for claim_index, belief_score in enumerate(claim_beliefs):
            var, val = self.claims[claim_index]
            var_beliefs[var][val] = belief_score
        return var_beliefs

    @classmethod
    def from_csv(cls, path):
        """
        Load a matrix from a CSV file
        :param path: path on disk to a CSV file
        :return: a Dataset object representing the matrix encoded by the CSV
        """
        return cls(np.genfromtxt(path, delimiter=",", usemask=True))
