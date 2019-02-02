from collections import namedtuple


#: Tuple to hold the results of truth-discovery.
#: `trust` is a list of source trust scores in the order sources appear in the
#: input.
#: `belief` is a list of dicts of the form {val: belief, ...} for each variable
Result = namedtuple("Result", ["trust", "belief"])
