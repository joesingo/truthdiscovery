import numpy as np
import numpy.ma as ma

from truthdiscovery.input.supervised_dataset import SupervisedDataset


class SyntheticDataset(SupervisedDataset):
    """
    A synthetic dataset generated randomly according to given source trust
    values, each of which is interpreted as the probability that a source's
    claim is correct
    """
    def __init__(self, trust, num_variables=100, claim_probability=0.5,
                 domain_size=4,
                 **kwargs):
        """
        :param trust: numpy array of trust values in [0, 1] for sources
        :param num_variables: the number of artificial variables to generate
        :param claim_probability: the probability of a source making a claim
                                  about the value of a given variable
        :param domain_size: the number of possible values each variable
                            may take
        """
        if trust.ndim != 1:
            raise ValueError("Trust vector must be one dimensional")
        if trust.shape[0] == 0:
            raise ValueError("No trust values provided")
        # Check that trust values are numbers in in [0, 1]
        if np.any(np.isnan(trust)) or np.any(trust < 0) or np.any(trust > 1):
            raise ValueError("Trust values must be in [0, 1]")
        if claim_probability <= 0 or claim_probability > 1:
            raise ValueError("Claim probability must be in (0, 1]")
        if domain_size <= 1:
            raise ValueError("Domain size must be greater than 1")

        self.trust = trust
        # Generate 'true' values for the variables uniformly from [0,...,d - 1]
        true_values = np.random.randint(0, domain_size, size=(num_variables,))

        sv_mat = ma.masked_all((len(trust), num_variables))
        for var, true_value in enumerate(true_values):
            claim_made = False
            # Loop to ensure that at least one claim is made for this variable
            while not claim_made:
                for source, trust_val in enumerate(trust):
                    if np.random.random_sample() <= claim_probability:
                        claim_made = True
                        # Source claims the correct value with probability
                        # trust_val, and chooses an incorrect value uniformly
                        # otherwise
                        wrong_prob = (1 - trust_val) / (domain_size - 1)
                        prob_dist = [wrong_prob] * domain_size
                        prob_dist[int(true_value)] = trust_val
                        # Draw claimed value from domain with above probability
                        # distribution
                        sv_mat[source, var] = np.random.choice(
                            range(domain_size),
                            p=prob_dist
                        )

        super().__init__(sv_mat, true_values, **kwargs)
