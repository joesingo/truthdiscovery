from collections import OrderedDict, namedtuple

import numpy as np
import numpy.ma as ma


#: A claim in this context is an statement of the form X=v where X is a
#: variable and v is a value. Here `var` is the index of the variable in the
#: original data, and `val` is the value.
Claim = namedtuple("Claim", ["var", "val"])


class SourceClaimMatrix:
    """
    A matrix containing data about which sources make which claims. Entries are
    0 or 1 to indicate whether a source (row) makes a claim (column) or not,
    i.e.  this is the adjacency matrix of the source/claims graph.
    """

    def __init__(self, sv_matrix):
        """
        Construct the matrix from a SourceVariableMatrix.

        Claims are constructed for each variable X by looking at all the
        distinct values v that sources claim this variable takes, and creating
        a claim to represent the statement 'X = v'.

        :param sv_matrix: SourceVariableMatrix to generate the claims matrix
                          from
        """
        self.sv_matrix = sv_matrix
        source_assertions = OrderedDict()

        for source, row in enumerate(self.sv_matrix.mat):
            for var, val in enumerate(row):
                if ma.is_masked(val):
                    continue

                claim = Claim(var, val)
                if claim not in source_assertions:
                    source_assertions[claim] = []
                source_assertions[claim].append(source)

        self.mat = np.zeros((self.num_sources(), len(source_assertions)))

        self.claims = []
        for j, (claim, sources) in enumerate(source_assertions.items()):
            self.claims.append(claim)
            for source in sources:
                self.mat[source, j] = 1

    def num_sources(self):
        """
        :return: the number of sources
        """
        return self.sv_matrix.num_sources()

    def num_claims(self):
        """
        :return: the number of claims
        """
        return self.mat.shape[1]

    def get_claim(self, claim_index):
        """
        :return: a Claim tuple representing the claim with the given column
                 index in the matrix
        """
        return self.claims[claim_index]
