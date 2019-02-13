import numpy as np
import numpy.ma as ma

from truthdiscovery.input.dataset import Dataset
from truthdiscovery.input.supervised_data import SupervisedData


class SyntheticData(SupervisedData):
    """
    A synthetic dataset generated randomly according to given source trust
    values, each of which is interpreted as the probability that a source's
    claim is correct
    """
    def __init__(self, trust, num_variables=100, claim_probability=0.5,
                 domain_size=4, **kwargs):
        """
        :param trust: numpy array of trust values in [0, 1] for sources
        :param num_variables: the number of artificial variables to generate
        :param claim_probability: the probability of a source making a claim
                                  about the value of a given variable
        :param domain_size: the number of possible values each variable
                            may take
        :raises ValueError: if invalid parameters are given
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

        # Generate 'true' values for the variables uniformly from [0,...,d - 1]
        true_values = np.random.randint(0, domain_size, size=(num_variables,))

        sv_mat = ma.masked_all((len(trust), num_variables))
        for var, true_value in enumerate(true_values):
            claim_made = False
            for source, trust_val in enumerate(trust):
                if np.random.random_sample() <= claim_probability:
                    claim_made = True
                    sv_mat[source, var] = self.generate_claim(
                        trust_val, true_value, domain_size
                    )
            # Make sure at least one source makes a claim about this variable
            if not claim_made:  # pragma: no cover
                source = np.random.randint(0, len(trust))
                sv_mat[source, var] = self.generate_claim(
                    trust[source], true_value, domain_size
                )

        # Make sure all sources make at least one claim
        for source, row in enumerate(sv_mat):
            if row.mask.all():  # pragma: no cover
                var = np.random.randint(0, num_variables)
                sv_mat[source, var] = self.generate_claim(
                    trust[source], true_values[var], domain_size
                )

        super().__init__(Dataset(sv_mat), true_values, **kwargs)

    @classmethod
    def generate_claim(cls, trust_val, true_value, domain_size):
        """
        Generate a value for a source to claim for a variable
        :param trust_val: trust value for the source in [0, 1]
        :param true_value: the true value for the variable
        :param domain_size: the number of possible values for the variable; the
                            domain is {0, 1, ..., domain_size - 1}
        """
        # Source claims the correct value with probability trust_val, and
        # chooses an incorrect value uniformly otherwise
        wrong_prob = (1 - trust_val) / (domain_size - 1)
        prob_dist = [wrong_prob] * domain_size
        prob_dist[int(true_value)] = trust_val
        # Draw claimed value from domain with above probability distribution
        return np.random.choice(range(domain_size), p=prob_dist)
