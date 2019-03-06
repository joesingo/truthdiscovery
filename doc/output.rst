.. _output-page:

Output
======

The output of a truth-discovery algorithm in this library is a :any:`Result`
object. The most important attributes of :any:`Result` objects are ``trust``
and ``belief``, which are dictionaries containing the trust and belief scores
for each source and claim. See the example below for their format.

An important method is :any:`get_most_believed_values`, which returns (a
generator of) the values with highest belief score for a given variable.

See the :any:`Result` class for full documentation on the available attributes
and methods. The example below shows the format of the trust and belief
dictionaries, after running an algorithm on the first example dataset from
:ref:`input-page`.

    >>> results = AverageLog().run(mydata)
    >>> results.trust
    {'source 1': 0.2637321368777009, 'source 2': 0.52146101879096, 'source 3':
    0.7681758936725634, 'source 4': 1.0}
    >>> results.belief["x"]
    {4: 0.14915492164635274, 3: 1.0}
    >>> results.belief["y"]
    {7: 0.4440695965138328, 6: 0.5655545941885707}
    >>> results.belief["z"]
    {5: 0.7293600806789093, 8: 0.5655545941885707}
    >>> results.time_taken
    0.006222724914550781
    >>> results.iterations
    20
    >>> list(results.get_most_believed_values("x"))
    [3]
    >>> list(results.get_most_believed_values("y"))
    [6]
    >>> list(results.get_most_believed_values("z"))
    [5]
    >>> results.filter(sources=["source 1", "source 3"]).trust
    {'source 1': 0.2637321368777009, 'source 3': 0.7681758936725634}
    >>> results.filter(variables=["x"]).belief
    {'x': {4: 0.14915492164635274, 3: 1.0}}
    >>> results.get_trust_stats()
    (0.6383422623353061, 0.2746120273343826)
