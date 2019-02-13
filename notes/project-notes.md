## Implementation ideas:
Could have multiple interfaces:
  * Command line
  * Website
  * Python API
  * HTTP API?

Should have core Python API, from which command line and web clients are built
from. If necessary, a HTTP API can mimic the Python API.

Basic usage will be:
  * Choose algorithm
  * Choose algorithm parameters/initial conditions (algorithm-specific)
  * Upload/select dataset and any other inputs
    * Add option to specify number of sources/variables, and fill in matrix
      incrementally
  * Choose form of results
    * Table listing *all* belief and trust values
    * Values for sources/facts/objects matching a query

# Existing software

* This python library implements some fact-finding algorithms:
  https://github.com/totucuong/spectrum

## Fact-finding background

* Gupta survey has good background information, and lists many algorithms

* Homogeneous vs heterogeneous
  * Homogeneous: entities are all of the same type, and we have information
  about relationships between them (e.g. agent 1 trusts agent 2 to degree 0.6,
  or page 1 recommends page 2). Also called *reputation networks*

  * Heterogeneous: models multiple types of entities: most commonly *sources*
  make *claims* about *objects*

  * May also model claims about objects as sources stating the *value* of
  *variables*

* Most models output *trustworthiness* of sources, and *confidence* or
  *believability* of claims

  * Values in [0,1], but often without meaningful semantics (i.e. not
    probabilities)
  * Pasternack thesis also outputs user-specific *bias* and *completeness*
    scores (chapter 3)

* Some approaches also deal with *copying detection* in sources: determine if
  sources that copy each other, and which sources are dependent on which others
  (see [1] and [2] section 4)
  * Useful because false values are often copied between sources: commonly
    occurring claims might not be accurate

* Basic algorithms use only sources and claims as inputs:
  * Sums (Hubs and Authorities)
  * TruthFinder
  * Average.Log
  * 3-Estimates
  * Investment
  * PooledInvestment
  * Optimisation based methods (see 2015 survey, 2.2.2)

* Generalised and constrained fact-finding (see Pasternack thesis 4.5)
  * Includes additional information

  * Generalised:
    * Weights of claims (can model uncertainty in claim extraction process, or
      uncertainty in the claim itself)
    * Groups in the sources (sources implicitly support claims made by other
      sources in the same group)
    * Similarity in the claims (sources implicitly support similar claims)

  * Constrained:
    * Include (user specific) prior knowledge about what is true

* Semi-supervised
  * Uses a number of ground truths
  * E.g. [3]

## Ideas for truth-discovery properties and axioms

* Source makes an extra claim, not contradictory with other claims: scores
  remain the same
  * As it stands this is probably not sensible, since making an additional
    *bad* claim (e.g.  one whose other sources are not trustworthy) should
    decrease the trust score.

  * However could probably would make sense to say that making an additional
    claim *not made by anybody* else should never decrease trust score

  * Possibly even: new claim by a more trustworthy source than s: s's trust
    increases; by a less trustworthy source: s's trust decreases

* Changes outside a set of sources/claims: scores remain the same for the
  unchanged sources/claims

* Relabelling/reordering the sources/claims should have no affect on the scores

* Sources make identical claims: same trust scores

* Stability measure: upper bound on amount of change when k changes in input
  graph (matrix norm of difference between old and new trust matrices?)

* Main axiom: replacing one of a claim's sources with one with lower trust
  score results in lower confidence. Dually, replacing one of a source's claims
  with a less believable one results in lower trust score
  * Precisely: let c_1, c_2 be claims not made by a source s, and
    belief(c_1) <= belief(c_2). Consider new graphs G_1 where s claims c_1, and
    G_2 where s claims c_2. Then trust(G_1, s) <= trust(G_2, s)
  * Similar in the other direction, where we add two sources to a claim

* PageRank axioms could apply to homogeneous networks

* If claims state that a variable X takes a given value: trust/belief scores
  should not depend on the specific values that sources claim X takes; i.e.
  replacing all claims X=k with X=k' leaves scores unchanged.

* If all sources make the same claim, that claim should be the most believed.

## Future work

* Encode a set of *integrity constraints*:
  * For binary variables (i.e. atomic claims), encode a set of propositional
  formulas that determine whether a possible world (assignment of true/false to
  each claim) is *feasible*
  * Would be interesting to handle cases whether most believable world (as
  given by a truth-discovery algorithm) is not feasible
  * Pasternack and Roth paper deals with this as part of iterative algorithms
  * TruthFinder (in a sense) has this in a fuzz way by modelling implications
  between facts, but I think this encodes that certain worlds are *unlikely*,
  not infeasible

## Papers

1. Xin Luna Dong, Laure Berti-Equille, and Divesh Srivastava
   Truth discovery and copying detection in a dynamic world
   PVLDB, 2(1):562–573, 2009

2. Manish Gupta, Jiawei Han
   Heterogeneous Network-Based Trust Analysis: A Survey

3. Xiaoxin Yin, Wenzhao Tan
   Semi-supervised Truth Discovery
