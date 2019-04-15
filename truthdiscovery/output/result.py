import copy

import numpy as np

from truthdiscovery.utils import filter_dict


class Result:
    """
    Object to hold the results of truth discovery.
    """
    def __init__(self, trust, belief, time_taken, iterations=None):
        """
        :param trust:  a mapping of the form ``{source_label: trust_val, ..}``
                       containing trust values for sources
        :param belief: a mapping of the form
                       ``{var_label: {val: belief, ...}, ...}`` containing
                       belief values for claims
        :param time_taken: seconds taken to produce these results
        :param iterations: number of iterations the algorithm ran for, or None
                           if not applicable
        """
        self.trust = trust
        self.belief = belief
        self.time_taken = time_taken
        self.iterations = iterations

    def get_most_believed_values(self, var):
        """
        Compute the most believed values for a variable. Note that more than
        one value may be most-believable if there are ties for maximum belief.

        :param var: label of the variable to consider
        :return: a generator of the values with maximum belief
        """
        sorted_beliefs = sorted(self.belief[var].items(), key=lambda x: -x[1])
        max_belief = sorted_beliefs[0][1]

        for val, belief in sorted_beliefs:
            if belief < max_belief:
                break
            yield val

    def filter(self, sources=None, variables=None):
        """
        Filter a set of results to only include trust and belief scores for
        subsets of the sources and variables

        :param sources:   iterable of source labels to narrow the trust scores
                          down to, or None to perform no source filtering
        :param variables: iterable of variable labels to narrow the belief
                          scores down to, or None to perform no variable
                          filtering
        :return: a :any:`Result` object with trust/belief scores for only the
                 requested sources and variables
        """
        new_scores = []
        filters = ((sources, self.trust), (variables, self.belief))
        for filter_set, full_scores in filters:
            if filter_set is not None:
                new_scores.append(dict(filter_dict(full_scores, filter_set)))
            else:
                new_scores.append(copy.deepcopy(full_scores))
        new_trust, new_belief = new_scores

        return Result(new_trust, new_belief, self.time_taken, self.iterations)

    def _get_stats(self, scores_dict):
        """
        :return: ``(mean, stddev)`` of values in ``scores_dict``
        """
        scores_vec = np.fromiter(
            scores_dict.values(), dtype=np.float64, count=len(scores_dict)
        )
        return (np.mean(scores_vec), np.std(scores_vec))

    def get_trust_stats(self):
        """
        :return: a tuple ``(mean, stddev)`` of the mean and standard deviation
                 of trust scores
        """
        return self._get_stats(self.trust)

    def get_belief_stats(self):
        """
        :return: a dictionary of the form ``{var_label: (mean, stddev), ...}``
                 containing mean and standard deviation of belief scores for
                 each variable
        """
        return {
            var: self._get_stats(scores) for var, scores in self.belief.items()
        }
