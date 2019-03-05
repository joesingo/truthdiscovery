# truthdiscovery

`truthdiscovery` is a Python3 library that implements various truth-discovery
algorithms.

A truth-discovery problem consists of

* a number of *sources*
* a number of *objects*
* for each source, a set of *claims* made by the source, with each claim
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

## Supported algorithms
* Majority voting (baseline algorithm)
* Sums [1]
* Average.Log [1]
* Investment [1]
* PooledInvestment [1]
* TruthFinder [2]

## Input

In this library, objects are referred to as *variables*, and claims are
statements asserting that a given variable takes a given value.

The data is then given as a list (or other iterable) of tuples of the form
``(source_label, var_label, value)``.

Alternatively, if all values are numeric, the source/claim/variable network can
be encoded as a matrix where rows correspond to sources, columns correspond to
variables, and an entry at position ``(i, j)`` is the value that source ``i``
claims for variable ``j`` (the matrix may contain empty cells in cases where a
source does not make a claim about a variable).

## Installation

This package should be installed with `pip` (using Python 3). It is recommended
to work in a [virtualenv](https://docs.python.org/3/tutorial/venv.html) to
avoid conflicts with globally-installed packages:

```
$ cd <repo root>
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -e .
```

## Usage

TODO

## References
1. Pasternack, Jeff and Roth, Dan, [*"Knowing What to Believe (when You Already
   Know Something)"*](http://dl.acm.org/citation.cfm?id=1873781.1873880)

1. X. Yin and J. Han and P. S. Yu [*"Truth Discovery with Multiple Conflicting
   Information Providers on the Web"*](http://ieeexplore.ieee.org/document/4415269/)
