class ResultDiff:
    """
    Object to represent the difference between two :any:`Result` objects.
    Has attributes for differences in source trusts, claim beliefs, time taken
    and number of iterations
    """
    def __init__(self, res1, res2):
        self.trust = {}
        self.belief = {}
        self.time_taken = res2.time_taken - res1.time_taken
        self.iterations = None

        sources1 = res1.trust.keys()
        sources2 = res2.trust.keys()
        common_sources = set(sources1).intersection(sources2)
        for source in common_sources:
            self.trust[source] = res2.trust[source] - res1.trust[source]

        vars1 = res1.belief.keys()
        vars2 = res2.belief.keys()
        common_vars = set(vars1).intersection(vars2)
        for var in common_vars:
            diffs = {}
            vals1 = set(res1.belief[var].keys())
            vals2 = set(res2.belief[var].keys())
            common_vals = vals1.intersection(vals2)
            for val in common_vals:
                diffs[val] = res2.belief[var][val] - res1.belief[var][val]
            if diffs:
                self.belief[var] = diffs

        if res1.iterations is not None and res2.iterations is not None:
            self.iterations = res2.iterations - res1.iterations
