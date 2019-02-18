from bidict import bidict
import numpy.ma as ma

from truthdiscovery.input.dataset import Dataset


class TextDataset(Dataset):
    """
    Dataset class that is loaded from a text file, and where source/variable
    names and variable values may be strings.

    This is a base class that provides common functionality: for specific text
    formats this class should be sub-classed and the :any:`get_tuples` method
    implemented.
    """
    source_ids = None
    var_ids = None
    val_hashes = None

    def __init__(self, fileobj):
        """
        :param fileobj: file object to read data from
        """
        # Create incremental integer IDs for source and variable labels (which
        # may be strings or other objects), and integer 'hash values' per
        # (variable, value) pair.
        #
        # Use a bi-directional mapping from bidcit
        self.source_ids = bidict()
        self.var_ids = bidict()
        self.val_hashes = bidict()

        # Build the source-variables matrix
        sv_entries = []
        for source_label, var_label, val in self.get_tuples(fileobj):
            # Create new source/variable IDs or value hashes if necessary
            if source_label not in self.source_ids:
                self.source_ids[source_label] = len(self.source_ids)

            if var_label not in self.var_ids:
                self.var_ids[var_label] = len(self.var_ids)

            if (var_label, val) not in self.val_hashes:
                self.val_hashes[(var_label, val)] = len(self.val_hashes)

            # Record this entry in SV matrix
            s_id = self.source_ids[source_label]
            var_id = self.var_ids[var_label]
            val_hash = self.val_hashes[(var_label, val)]
            sv_entries.append((s_id, var_id, val_hash))

        sv_mat = ma.masked_all((len(self.source_ids), len(self.var_ids)))
        for source, var, val in sv_entries:
            sv_mat[source, var] = val

        super().__init__(sv_mat)

    # def get_variable_value_beliefs(self, claim_beliefs):
    #     # Override this method to convert integer variable names/values to the
    #     # real labels
    #     orig_beliefs = super().get_variable_value_beliefs(claim_beliefs)
    #     var_beliefs = {}
    #     for var_id, beliefs in enumerate(orig_beliefs):
    #         var_label = self.var_ids.inverse[var_id]
    #         this_beliefs = {}
    #         for val_hash, belief in beliefs.items():
    #             _, val = self.val_hashes.inverse[val_hash]
    #             this_beliefs[val] = belief
    #         var_beliefs[var_label] = this_beliefs
    #     return var_beliefs

    def get_tuples(self, fileobj):
        """
        Return an iterable of (source, variable, value) tuples from the input
        file. The data types for each item in the tuples must be hashable.

        :param fileobj: file object to read data from
        :raises NotImplementedError:
        """
        raise NotImplementedError("Must be implemented in child classes")
