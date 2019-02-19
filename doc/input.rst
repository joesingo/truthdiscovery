.. _input-page:

Input Data
==========

In this library, the input to a truth-discovery algorithm is a :any:`Dataset`
object. A dataset object is constructed by passing an iterable of tuples of the
form ``(source_label, var_label, value)`` for each claim that is made.

For example, consider the following situation:

- Source 1 claims X = 4, Y = 7
- Source 2 claims Y = 7, Z = 8
- Source 3 claims X = 3, Z = 5
- Source 4 claims X = 3, Y = 6, Z = 8

This dataset can be constructed as follows. ::

    from truthdiscovery import Dataset
    tuples = [
        ("source 1", "x", 4),
        ("source 1", "y", 7),
        ("source 2", "y", 7),
        ...
    ]
    mydata = Dataset(tuples)

In this case all values are numeric, so the dataset can alternatively be
created as a :any:`MatrixDataset`. This is done by giving a matrix where rows
correspond to sources, columns correspond to variables, and an entry at
position ``(i, j)`` is the value that source ``i`` claims for variable ``j``
(the matrix may contain empty cells in cases where a source does not make a
claim about a variable).

In matrix form, the above example is is:

.. math::
   \begin{bmatrix}
   4 & 7 & - \\
   - & 7 & 8 \\
   3 & - & 5 \\
   3 & 6 & 8 \\
   \end{bmatrix}

where the columns correspond to X, Y and Z respectively. Note that the sources
and variable are not explicitly assigned labels (e.g. ``source 1``, ``x``) as
they are when using the :any:`Dataset` constructor.

Matrices are representing using numpy's *masked array* type; the above example
can be constructed as follows. ::

   import numpy.ma as ma
   from truthdiscovery import MatrixDataset

   mydataset = MatrixDataset(ma.masked_values([
       [4, 7, 0],
       [0, 7, 8],
       [3, 0, 5],
       [3, 6, 8]
   ], 0))

:any:`MatrixDataset` objects can also be loaded from a file using the
:meth:`~truthdiscovery.input.matrix_dataset.MatrixDataset.from_csv` method. The
above dataset in CSV format would be::

    4,7,
    ,7,8
    3,,5
    3,6,8

Advanced input
--------------

TODO:

- Explain claim implications

Datasets with known true values
-------------------------------

An easy way to evaluate the performance of a truth-discovery algorithm is to
run it on a dataset for which the true values of some of the variables is
already known. A measure of the *accuracy* of the algorithm can then be
computed by considering how many variables the algorithm predicted the correct
value (i.e. the most believed value for a variable was the correct one).

To this end, the :any:`SupervisedData` class stores a :any:`Dataset` along with
known true variable values as a dictionary in the form
``{var_label: true_value, ...}``. For example: ::

    from truthdiscovery import SupervisedData

    supervised = SupervisedData(mydataset, {"x": 4, "y": 5})

    # run an algorithm and compute accuracy...

    accuracy = supervised.get_accuracy(results)

See :meth:`~truthdiscovery.input.supervised_data.SupervisedData.get_accuracy`
for a description of how the accuracy calculation is performed.

Supervised data can also be loaded from a matrix in a CSV file. The format is
the same as for unsupervised matrix data (see above), but the first row
contains the true values.

Synthetic data
--------------

TODO: explain

- Purpose of synthetic data
- Method of generation
- Available parameters
- Export to CSV

Custom dataset formats
----------------------

TODO:

- Explain FileDataset
- Give examples
