class Result:
    """
    Object to hold the results of truth-discovery.
    """
    def __init__(self, trust, belief):
        """
        :param trust:  a mapping of the form ``{source_label: trust_val, ..}``
                       containing trust values for sources
        :param belief: a mapping of the form
                       ``{var_label: {val: belief, ...}, ...}`` containing
                       belief values for claims
        """
        self.trust = trust
        self.belief = belief

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
