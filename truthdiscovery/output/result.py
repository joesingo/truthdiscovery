class Result:
    """
    Object to hold the results of truth-discovery.
    """
    def __init__(self, trust, belief):
        """
        :param trust:  a list of source trust scores in the order sources
                       appear in the input.
        :param belief: a list of dicts of the form ``{val: belief, ...}`` for
                       each variable
        """
        self.trust = trust
        self.belief = belief

    def get_most_believed_values(self, var):
        """
        Compute the most believed values for a variable. Note that more than
        one value may be most-believable if there are ties for maximum belief.

        :param var: index in the input data of the variable to consider
        :return: a generator of the values with maximum belief
        """
        sorted_beliefs = sorted(self.belief[var].items(), key=lambda x: -x[1])
        max_belief = sorted_beliefs[0][1]

        for val, belief in sorted_beliefs:
            if belief < max_belief:
                break
            yield val
