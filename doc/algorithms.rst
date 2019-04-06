.. _algorithms-page:

Algorithms
==========

The algorithms implemented in this library are:

- Majority voting (baseline algorithm)
- Sums [1]_
- Average.Log [1]_
- Investment [1]_
- PooledInvestment [1]_
- TruthFinder [2]_

Each algorithm is represented by a class. Usage is roughly as follows. ::

    alg = AlgorithmClass(param1=val1, ...)
    results = alg.run(mydata)

The available parameters depend on the algorithm, and are listed in detail
below. See :ref:`output-page` for details on the format of the results as
returned by the :meth:`~truthdiscovery.algorithm.base.BaseAlgorithm.run`
method.

.. _majority-voting:

Majority voting
---------------
Majority voting is a simple baseline algorithm where all sources are assigned a
trust score of 1, and the belief score for a variable taking a given value
is simply the number of sources who make that assertion, divided by the maximum
number of sources for a claim (to ensure all belief scores are between 0 and
1). There are no optional parameters. ::

    from truthdiscovery import MajorityVoting
    voting = MajorityVoting()
    results = voting.run(data)

Iterative algorithms
--------------------
Apart from majority voting, all algorithms are *iterative*, in that they
initialise the trust and belief scores to initial values, and iteratively
update them until some stopping criterion is satisfied.

Optional parameters common to all iterative algorithms are:

- ``iterator``: this controls the mode of iteration and the stopping criterion.
  It should be an :any:`Iterator` instance. There are two types of iterator
  available: :any:`FixedIterator`, where a fixed number of iterations are
  performed, and :any:`ConvergenceIterator`, where iteration continues until
  the distance between successive trust scores becomes lower than a given
  threshold.

  Unless otherwise stated, the default ``iterator`` is a :any:`FixedIterator`
  for 20 iterations.

- ``priors``: this determines the 'prior belief' scores, i.e. initial belief
  score for each claim. See :any:`PriorBelief` for the available choices.

  Unless otherwise stated, the default for ``priors`` is
  :any:`PriorBelief.FIXED`.

As well as returning final results with ``alg.run(mydata)``, iterative
algorithms support returning an iterable of partial results as the algorithm
iterates with :any:`run_iter` : ::

    from truthdiscovery import Sums
    alg = Sums()
    for results in alg.run_iter(mydata):
        print("Trust at iteration {}".format(results.iterations))
        print(results.trust)

For each of the algorithms below, please refer to the cited paper for details
on how the algorithm operates and the meaning of any additional optional
parameters.

Sums and Average.Log
~~~~~~~~~~~~~~~~~~~~
Both algorithms were introduced by Pasternack and Roth [1]_, and do not accept
any additional parameters.

Investment and PooledInvestment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Also introduced by Pasternack and Roth [1]_, both accept an optional parameter
``g``, which defaults to 1.2 for *Investment* and 1.4 for *PooledInvestment*.

``priors`` defaults to :any:`PriorBelief.VOTED` for *Investment* and
:any:`PriorBelief.UNIFORM` for *PooledInvestment*.

TruthFinder
~~~~~~~~~~~
Introduced in by Yin et. al. [2]_, *TruthFinder* has the following optional
parameters:

- ``influence_param`` (:math:`\rho` in the paper, default: 0.5)
- ``dampening_factor`` (:math:`\gamma` in the paper, default: 0.3)
- ``initial_trust`` (default: 0.9)

The default mode of iteration is until convergence in
:any:`DistanceMeasures.COSINE` with threshold 0.001.

Unlike the other algorithms, *TruthFinder* always initialises the trust vector
to fixed values (see ``initial_trust``) instead of the belief vector, so
``priors`` is not applicable.

Examples
~~~~~~~~

::

    from truthdiscovery import (
        AverageLog,
        ConvergenceIterator,
        FixedIterator,
        Investment,
        MajorityVoting,
        PooledInvestment,
        Sums,
        TruthFinder
    )

    # Perform 35 iterations, VOTED priors
    alg1 = Sums(iterator=FixedIterator(35), priors=PriorBelief.VOTED)

    # Iterate until L1 distance is less than 0.01
    alg2 = AverageLog(iterator=ConvergenceIterator(DistanceMeasures.L1, 0.01))

    # Iterate until convergence, but no more than 100 iterations
    # A ConvergenceError exception is raised if convergence within
    # 0.01 is not achieved within 100 iterations
    myit = ConvergenceIterator(DistanceMeasures.L_INF, 0.01, limit=100)
    alg3 = Investment(iterator=myit, g=1.15)

References
----------
.. [1] Pasternack, Jeff and Roth, Dan, `Knowing What to Believe (When You
   Already Know Something)
   <http://dl.acm.org/citation.cfm?id=1873781.1873880>`_.

.. [2] X. Yin and J. Han and P. S. Yu, `Truth Discovery with Multiple Conflicting
   Information Providers on the Web
   <http://ieeexplore.ieee.org/document/4415269/>`_.
