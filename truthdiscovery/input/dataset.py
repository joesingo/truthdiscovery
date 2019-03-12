import itertools

from bidict import bidict
import scipy.sparse


class IDMapping(bidict):
    """
    Bi-directional mapping from *labels* (of arbitrary type) to integer IDs
    """
    def get_id(self, label, insert=True):
        """
        :param label:  label to return ID for
        :param insert: if True, create a new ID for ``label`` if it is not
                       already present (default: True)
        :return: the ID for the ``label``
        :raises KeyError: if ``insert=False`` and ``label`` is not present
        """
        if label not in self and insert:
            self[label] = len(self)
        return self[label]


class Dataset:
    """
    An object to represent a dataset upon which truth-discovery will be
    performed. A dataset consists *variables* and the values they take
    according to different *sources*.

    Input is given as an iterable of tuples of the form
    ``(source_label, var_label, value)``. Labels and values in these tuples
    may be of any type that can be used as keys in a dict.

    Optionally the dataset may include implication values between claims about
    the same variable (e.g. for TruthFinder).

    The implication between claims ``var = x`` and ``var = y`` is a value in
    [-1, 1] that describes how the confidence that ``var = x`` influences the
    confidence of ``var = y``.  A positive value indicates that if ``var = x``
    is true, then ``var = y`` is likely to be true. A negative value means that
    if ``var = x`` is true, then ``var = y`` is likely to be false (Yin et.
    al., 2008).
    """
    source_ids = None
    var_ids = None
    claim_ids = None
    val_hashes = None

    def __init__(self, triples, implication_function=None):
        """
        :param triples: iterable of ``(source_label, var_label, value)`` as
                        described above
        :param implication_function: (optional) function to compute implication
                                     values between claims (see above). This
                                     should take ``(var, val1, val2)`` as
                                     arguments and return an implication value
                                     in [-1, 1], or None
        """
        self.source_ids = IDMapping()  # Map source label to integer IDs
        self.var_ids = IDMapping()     # Variable labels to IDs
        self.val_hashes = IDMapping()  # Values to IDs (hashes)
        self.claim_ids = IDMapping()   # (var_id, val_hash) tuples to IDs

        # Keep track of (source, var) pairs to detect if a source makes more
        # than one claim for a single variable
        source_var_pairs = {}

        # Keep track of (source_id, claim_id) pairs to populate the
        # source-claims matrix. Source and claim IDs for each pair are stored
        # in the same position in *separate lists*, since this is the format
        # the sparse matrix constructor requires
        sc_rows = []
        sc_cols = []

        # Keep track of all claims IDs for each variable, to populate the
        # mutual exclusion matrix. The keys are variable IDs, and values are
        # sets of claim IDs
        mut_ex_claims = {}

        for source_label, var_label, val in triples:
            s_id = self.source_ids.get_id(source_label)
            var_id = self.var_ids.get_id(var_label)
            val_hash = self.val_hashes.get_id(val)

            if (s_id, var_id) in source_var_pairs:
                raise ValueError(
                    "Source '{}' claimed more than one value for variable '{}'"
                    .format(self.source_ids.inverse[s_id],
                            self.var_ids.inverse[var_id])
                )
            source_var_pairs[(s_id, var_id)] = True

            claim = (var_id, val_hash)
            claim_id = self.claim_ids.get_id(claim)
            sc_rows.append(s_id)
            sc_cols.append(claim_id)

            if var_id not in mut_ex_claims:
                mut_ex_claims[var_id] = set()
            mut_ex_claims[var_id].add(claim_id)

        self.num_sources = len(self.source_ids)
        self.num_variables = len(self.var_ids)
        self.num_claims = len(self.claim_ids)

        # Create source-claim matrix: entry (i, j) is 1 if source i makes claim
        # j, and 0 otherwise
        self.sc = scipy.sparse.csr_matrix(
            ([1] * len(sc_rows), (sc_rows, sc_cols)),
            shape=(self.num_sources, self.num_claims)
        )

        # Create mutual exclusion matrix: entry (i, j) is 1 if claims i and j
        # relate to the same variable (including when i=j) and 0 otherwise
        mut_ex_rows = []  # Construct in the same way as for sc
        mut_ex_cols = []
        for claim_ids in mut_ex_claims.values():
            for i, j in itertools.product(claim_ids, repeat=2):
                mut_ex_rows.append(i)
                mut_ex_cols.append(j)

        self.mut_ex = scipy.sparse.csr_matrix(
            ([1] * len(mut_ex_rows), (mut_ex_rows, mut_ex_cols)),
            shape=(self.num_claims, self.num_claims)
        )

        # Create implication matrix, for implications between claims
        imp_rows = []
        imp_cols = []
        imp_entries = []
        if implication_function is not None:
            # Iterate over non-zero entries in mut ex
            for j1, j2 in zip(*self.mut_ex.nonzero()):
                if j1 == j2:
                    continue
                # Note that claims j1 and j2 are for the same variable, since
                # mut ex is 1 at this point
                var_id, val1_hash = self.claim_ids.inverse[j1]
                _, val2_hash = self.claim_ids.inverse[j2]

                var = self.var_ids.inverse[var_id]
                val1 = self.val_hashes.inverse[val1_hash]
                val2 = self.val_hashes.inverse[val2_hash]
                imp_value = implication_function(var, val1, val2)

                if imp_value is not None:
                    if imp_value < -1 or imp_value > 1:
                        raise ValueError(
                            "Implication values must be in [-1, 1]"
                        )
                    imp_entries.append(imp_value)
                    imp_rows.append(j1)
                    imp_cols.append(j2)

        if imp_entries:
            self.imp = scipy.sparse.csr_matrix(
                (imp_entries, (imp_rows, imp_cols)),
                shape=(self.num_claims, self.num_claims)
            )
        else:
            self.imp = scipy.sparse.csr_matrix(
                (self.num_claims, self.num_claims)
            )

    def get_belief_dict(self, claim_beliefs):
        """
        Convert belief in claims to belief in (var, val) pairs.

        :param belief: numpy array of belief values for claims, ordered by
                       claim ID
        :return:       a dict of belief values for variables taking different
                       values, in the format required for :any:`Result`
        """
        var_beliefs = {}
        for claim_id, belief_score in enumerate(claim_beliefs):
            var_id, val_hash = self.claim_ids.inverse[claim_id]
            var_label = self.var_ids.inverse[var_id]
            val = self.val_hashes.inverse[val_hash]
            if var_label not in var_beliefs:
                var_beliefs[var_label] = {}
            var_beliefs[var_label][val] = belief_score
        return var_beliefs

    def get_source_trust_dict(self, trust):
        """
        :param trust: numpy array of source trust values, ordered by source ID
        :return:      a dict of source trusts in the format required for
                      :any:`Result`
        """
        return {
            self.source_ids.inverse[i]: trust_val
            for i, trust_val in enumerate(trust)
        }
