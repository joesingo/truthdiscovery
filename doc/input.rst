.. _input-page:

Input Data
==========

In this library, the input to a truth-discovery algorithm is a matrix where
rows correspond to sources, columns correspond to variables, and an entry at
position ``(i, j)`` is the value that source ``i`` claims for variable ``j``
(the matrix may contain empty cells in cases where a source does not make a
claim about a variable).

For example, consider the following situation:

- Source 1 claims X = 4, Y = 7
- Source 2 claims Y = 7, Z = 8
- Source 3 claims X = 3, Z = 5
- Source 4 claims X = 3, Y = 6, Z = 8

In matrix form, this is:

.. math::
   \begin{bmatrix}
   4 & 7 & - \\
   - & 7 & 8 \\
   3 & - & 5 \\
   3 & 6 & 8 \\
   \end{bmatrix}

where the columns correspond to X, Y and Z respectively.

Basic Usage
-----------

Datasets are represented by the :any:`Dataset` class. The above data can be
loaded as follows. ::

   import numpy.ma as ma
   from truthdiscovery.input import Dataset

   mydataset = Dataset(ma.masked_values([
       [4, 7, 0],
       [0, 7, 8],
       [3, 0, 5],
       [3, 6, 8]
   ], 0))

Note that numpy's `masked array` type is used to represent a matrix with missing
entries.

:any:`Dataset` objects can also be loaded from a file using the
:meth:`~truthdiscovery.input.dataset.Dataset.from_csv` method. The above
dataset in CSV format would be::

    4,7,
    ,7,8
    3,,5
    3,6,8

Advanced input types
--------------------

TODO:

- Explain :any:`ClaimImplicationDataset`

Datasets with known true values
-------------------------------

An easy way to evaluate the performance of a truth-discovery algorithm is to
run it on a dataset for which the true values of some of the variables is
already known. A measure of the `accuracy` of the algorithm can then be
computed by considering how many variables the algorithm predicted the correct
value (i.e. the most believed value for a variable was the correct one).

To this end, the :any:`SupervisedData` class stores a :any:`Dataset` along with
a list of true variable values. The list of true values may contain empty
values for cases where only a subset of true values are known. For example: ::

    from truthdiscovery.input import SupervisedData

    values = ma.masked_values([4, 5, 0], 0)
    supervised = SupervisedData(mydataset, values)

    # run an algorithm and compute accuracy...

    accuracy = supervised.get_accuracy(results)

See :meth:`~truthdiscovery.input.supervised_data.SupervisedData.get_accuracy`
for a description of how the accuracy calculation is performed.

Supervised data can also be loaded from a CSV file. The format is the same as
for unsupervised data (see above), but the first row contains the true values.

Synthetic data
--------------

TODO: explain

- Purpose of synthetic data
- Method of generation
- Available parameters
