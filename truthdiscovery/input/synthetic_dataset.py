import numpy as np
import numpy.ma as ma

from truthdiscovery.input.supervised_dataset import SupervisedDataset


class SyntheticDataset(SupervisedDataset):
    """
    A synthetic dataset generated randomly according to given source trust
    values
    """
    def __init__(self, trust, num_variables=100, claim_probability=0.5,
                 **kwargs):
        """
        :param trust: numpy array of trust values in [0, 1] for sources
        :param num_variables: the number of artificial variables to generate
        :param claim_probability: the probability of a source making a claim
                                  about the value of a given variable
        """
        if trust.ndim != 1:
            raise ValueError("Trust vector must be one dimensional")
        if trust.shape[0] == 0:
            raise ValueError("No trust values provided")
        # Check that trust values are numbers in in [0, 1]
        if np.any(np.isnan(trust)) or np.any(trust < 0) or np.any(trust > 1):
            raise ValueError("Trust values must be in [0, 1]")
        if claim_probability < 0 or claim_probability > 1:
            raise ValueError("Claim probability must be in [0, 1]")

        self.trust = trust
        num_sources = len(trust)
        # Generate 'true' values for the variables uniformly from {0, 1}
        true_values = np.random.randint(0, 1, size=(num_variables,))

        sv_mat = ma.masked_all((num_sources, num_variables))
        for source, trust_val in enumerate(trust):
            for var, true_value in enumerate(true_values):
                if np.random.random_sample() <= claim_probability:
                    if np.random.random_sample() <= trust_val:
                        # Guess correctly
                        sv_mat[source, var] = true_value
                    else:
                        sv_mat[source, var] = 1 if true_value == 0 else 1

        super().__init__(sv_mat, true_values, **kwargs)
