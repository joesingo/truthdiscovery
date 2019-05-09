# truthdiscovery

`truthdiscovery` is a Python3 library that implements various truth discovery
algorithms.

A truth discovery problem consists of

* a number of *sources*
* a number of *objects*
* for each source, a set of *claims* made by the source, with each claim
  relating to a distinct object

An object may be associated with multiple (conflicting) claims from different
sources, in which case it is not clear up front which is the true claim. It is
typically assumed that there is only one true claim for each object.

Truth discovery addresses this by using the network of sources, claims and
objects to determine the *trustworthiness* of sources, the *belief* in each
claim, and the true claim for each object.

The general principle for most algorithms is that trustworthy sources make
believably claims, and believable claims are made my trustworthy sources.

Most approaches are *unsupervised*, in that they do not use any prior knowledge
for the trustworthiness of sources etc.

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

## Usage and documentation

See the full documentation at [some-web-page](#) (**TODO**: host documentation
somewhere: until then see the `doc/` directory)
