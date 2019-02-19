# Convergence tests on synthetic data

The graph show how quickly each algorithm converges when applied to synthetic
data with 1000 sources and 1000 variables (where source trust values were drawn
from a uniform distribution on [0, 1]).

For iterative algorithms, the vector of source trust scores is updated at each
iteration. In the experiment the distance between the old and new trust vectors
was measured at each iteration -- this distance is plotted on the vertical axis
against the iteration number on the horizontal axis. Each algorithm was run for
30 iterations, or until the algorithm could no longer continue due to rounding
errors (this only happened for *TruthFinder*). Each algorithm was run several
times using different measures of distance: the $L_1$, $L_2$ and $L_{\infty}$
norms (Manhattan, Euclidean and maximum distances respectively), and 'cosine
distance', which is the cosine similarity subtracted from 1.

For most algorithms, the distance between old and new trust appears to decrease
exponentially, so a logarithmic scale is used for the vertical axis in order to
more clearly see the behaviour.

TODO:
- compare each algorithm
- note that distance getting small does not mean (mathematically) that vector
  will converge (e.g. partial sums of harmonic series)
