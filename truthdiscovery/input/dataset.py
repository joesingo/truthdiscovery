import itertools

from bidict import bidict
import numpy as np


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

        # Keep track of (source_id, claim_id) pairs to populate the
        # source-claims matrix
        sc_entries = []

        # Keep track of all claims IDs for each variable, to populate the
        # mutual exclusion matrix. The keys are variable IDs, and values are
        # lists of claim IDs
        mut_ex_claims = {}

        for source_label, var_label, val in triples:
            s_id = self.source_ids.get_id(source_label)
            var_id = self.var_ids.get_id(var_label)
            val_hash = self.val_hashes.get_id(val)

            claim = (var_id, val_hash)
            claim_id = self.claim_ids.get_id(claim)
            sc_entries.append((s_id, claim_id))

            if var_id not in mut_ex_claims:
                mut_ex_claims[var_id] = []
            mut_ex_claims[var_id].append(claim_id)

        self.num_sources = len(self.source_ids)
        self.num_variables = len(self.var_ids)
        self.num_claims = len(self.claim_ids)

        # Create source-claim matrix: entry (i, j) is 1 if source i makes claim
        # j, and 0 otherwise
        self.sc = np.zeros((self.num_sources, self.num_claims))
        for source, claim in sc_entries:
            self.sc[source, claim] = 1

        # Create mutual exclusion matrix: entry (i, j) is 1 if claims i and j
        # relate to the same variable (including when i=j) and 0 otherwise
        self.mut_ex = np.zeros((self.num_claims, self.num_claims))
        for claim_ids in mut_ex_claims.values():
            for i, j in itertools.product(claim_ids, repeat=2):
                self.mut_ex[i, j] = 1

        # Create implication matrix, for implications between claims
        self.imp = np.zeros((self.num_claims, self.num_claims))
        if implication_function is not None:
            for j1, j2 in np.argwhere(self.mut_ex == 1):
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
                    self.imp[j1, j2] = imp_value

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
