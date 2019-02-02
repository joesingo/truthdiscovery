Kleinburg paper on Hubs and Authorities:

## Hubs and Authorities: (aka Sums)
(Paper: http://www.cs.cornell.edu/home/kleinber/auth.pdf)

* Context is ranking web pages: find the most prominent pages
* Textual content of pages is not a good indicator of prominence: e.g. Honda
  website will not contain text 'automotive manufacturer'
* Use link structure of the web to infer which pages are 'best'
* Authoritative pages are linked to from many places
* However, having lots of in-links alone just means page is *popular*, not
  necessarily *authoritative*
* Authorities will have overlap in the sets of pages that link to them, since
  there are pages that act as *guides* or *resource lists* that link to the
  relevant authorities.
* These guide pages are referred to as *hubs*
* Each page given a *hub score* and an *authority score*: hub score of a page
  is the sum of the authority of the pages it links to, and authority score of
  a page is the sum of the hub scores of pages linking to it.
* Initialise all scores to 1, and compute iteratively.
* Scores will eventually converge
* (Note: can also be computed in terms of eigenvalues of certain matrices)

* Adapted to fact-finding (Pasternack et al refer to the algorithm as 'Sums'):
  - *sources* are seen as hubs, and *claims* are seen as authorities
  - hub score is replaced by *trustworthiness*, and authority score is *belief*
  in a claim
  - accordingly, claims made by trustworthy sources are more believable, and
  sources making believable claims are more trustworthy
  - a difference here is that there is more asymmetry: sources and claims are
  entirely different objects, whereas in H&A all objects are pages. we set the
  hub score of all claims and authority score of all sources to be 0 to reflect
  this

* Issues:
  - a source can become trustworthy by simply making many claims: e.g. a source
  making 1000 claims with belief score 0.5 is judged as more trustworthy as a
  source with 10 claims with belief score 0.95 (roughly)

## TRUTHFINDER

* Context: a set of *website* claim *facts* about *objects*
* Multiple websites may claim facts about the same object
* Facts may contradict or support each other: if website A says a book's author
  is J. Smith (fact f1), and website B claims John Smith (fact f2), then high
  confidence in f1 should increase confidence in f2 (and vice versa in this
  case). The situation is not always symmetric: consider f1: "author is J.
  Smith" and f2: "authors are J. Smith and P. Brown". Then f1 implies f2 in a
  sense, but f2 does not imply f1, since if f2 is true then there are two
  authors and f1 is incomplete.
* Define imp(f1 -> f2) as a number in [-1, 1] as a measure of how much
  confidence in f1 should increase (or decrease) confidence in f2
* Roughly:
  - treat confidence (belief) in a fact as the probability of it being
  correct
  - treat trustworthiness of a website as probability of its claims being
  correct: average of the probability of its claims

## Average.Log
(Pasternack and Roth: Knowing What to Believe (when you already know
something))

* As with Sums, but source trust scores are calculated as *average* claim belief
  multiplied by logarithm of number of claims made
* This prevents sources with low belief claims achieving high trust by simply
  making many claims; taking logarithm of number of claims is a 'diminishing
  returns'-type effect

## Investment
(Pasternack and Roth: Knowing What to Believe (when you already know
something))

* At time i, sources "invest" their trust T^i(s) uniformly across their claims
  (i.e. each claim receives T^i(s) / |C_s| from each of its sources)
* Claim beliefs grow according to a non-linear function (authors use x^1.2)
* Each claim yields a combined return of B^{i-1}(c) to its investors. Amount
  returned to source s is the fraction according to how much s invested in c
  relative to c's other sources

## PooledInvestment
(Pasternack and Roth: Knowing What to Believe (when you already know
something))

* Similar to Investment, but makes use of mutual exclusion groups to
  redistribute belief in claims across groups
* (I'm unsure of how to interpret their formula -- I cannot see how it matches
  the description in the text...)

## Cosine, 2-estimates, 3-estimates
(Galland et al: Corroborating Information from Disagreeing Views)

* Probabilistic model
* Aims to figure out which *facts* are true, given a number of *views* which
  claim several facts to be true or false
* Claims that a fact is false can be generated from prior knowledge of the fact
  (e.g. if a view claims 'Paris is the capital of France', they implicitly claim
  that 'X is the capital of France' is false for all X except Paris)
* Mutual exclusion groups of views can be generated from those views that
  disagree on a fact

### Cosine

* Iteratively estimates error of views (i.e. untrustworthiness) and truth
  values of facts in [-1, 1]
* For each view v (source), compute cosine similarity of the truth value of
  facts according to v, and the current predicted values (for the facts that v
  claims true or false). E.g. v says facts 1, 3, are true, 2 is false, and
  current predictions are 0.2, 1, -0.7 rep.; then we compute similarity of
  [1, -1, 1] and [0.2, 1, -0.7]

# Overview

Modelling truth-discovery problem as finding the values of variables X1...Xn
given claimed values v1...vn for each sources will henceforth be referred to as
*variables idea*.

* Sources and claims only:
  * *Sums, Average.Log, Investment*
  * Requires claims to be made by multiple sources to be useful
  * Variables idea: must only use discrete domains for variables, since
    otherwise it is unlikely that sources will make the same claims

* Sources, claims, and mutual exclusion groups:
  * *PooledInvestment*
  * Variables idea: mutual exclusion groups can be generated by considering
    claims in which a variable takes different values

* Sources, claims, objects, claim implications:
  * *TruthFinder*
  * Variables idea: objects would be variables. As with sources and claims
    only, domains should be discrete. Possibly implications between claims
    could be generated by considering difference in values (e.g. claim X=4
    implies X=4.05 more than it does X=10)

* Including difficulty of claims:
  * *3-estimates*
