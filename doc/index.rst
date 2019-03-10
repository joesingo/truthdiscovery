Welcome to truthdiscovery's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   input
   algorithms
   output

Overview
--------

``truthdiscovery`` is a Python3 library that implements various truth-discovery
algorithms.

A truth-discovery problem consists of

- a number of *sources*
- a number of *objects*
- for each source, a set of *claims* made by the source, with each claim
  relating to a distinct object

An object may be associated with multiple (conflicting) claims from different
sources, in which case it is not clear up front which is the true claim. It is
typically assumed that there is only one true claim for each object.

Truth-discovery addresses this by using the network of sources, claims and
objects to determine the *trustworthiness* of sources, the *belief* in each
claim, and the true claim for each object.

The general principle for most algorithms is that trustworthy sources make
believably claims, and believable claims are made my trustworthy sources.

Most approaches are *unsupervised*, in that they do not use any prior knowledge
for the trustworthiness of sources etc.

Installation
------------

This package should be installed with ``pip`` (using Python 3). It is recommended
to work in a `virtualenv <https://docs.python.org/3/tutorial/venv.html>`_ to
avoid conflicts with globally-installed packages::

    $ cd <repo root>
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -e .

Usage
-----

The command-line client can be used to run truth-discovery on a dataset in CSV
format: ::

    truthdiscovery run --algorithm sums --dataset mydata.csv

    # Change the default parameters
    truthdiscovery run --algorithm average_log --dataset mydata.csv \
        --params priors=uniform

    # Can give multiple parameters
    truthdiscovery run --algorithm investment --dataset mydata.csv \
        --params g=1.15 priors=fixed

    # Can use fixed or till-convergence iteration
    truthdiscovery run --algorithm truthfinder --dataset mydata.csv \
        --params iterator=fixed-200

    truthdiscovery run --algorithm truthfinder --dataset mydata.csv \
        --params iterator=l1-convergence-0.01

    truthdiscovery run --algorithm truthfinder --dataset mydata.csv \
        --params iterator=l_inf-convergence-0.01-limit-200

    # Restrict results to a subset of sources/variables
    truthdiscovery run --algorithm sums --dataset mydata.csv \
        --sources 0 3 --variables 1 2

See ``truthdiscovery --help`` and ``truthdiscovery run --help`` for detailed
usage.

Python API: ::

    >>> from truthdiscovery import Dataset, TruthFinder
    >>> mydata = Dataset([
    ...     ("source 1", "x", 4),
    ...     ("source 1", "y", 7),
    ...     ("source 2", "y", 7),
    ...     ("source 2", "z", 5),
    ...     ("source 3", "x", 3),
    ...     ("source 3", "z", 5),
    ...     ("source 4", "x", 3),
    ...     ("source 4", "y", 6),
    ...     ("source 4", "z", 8)
    ... ])
    >>> alg = TruthFinder()
    >>> results = alg.run(mydata)
    >>> # What is most likely value for x?
    ... set(results.get_most_believed_values("x"))
    {3}
    >>> # How trustworthy are the sources?
    ... results.trust
    {'source 1': 0.6519911420410474, 'source 2': 0.715051359018607, 'source 3':
    0.7125585145162463, 'source 4': 0.6283823616003958}

See :ref:`input-page` for how to construct different types of datasets,
:ref:`algorithms-page` to see which algorithms are available and the parameters
they can accept, and :ref:`output-page` for how to use the results returned
from an algorithm.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
