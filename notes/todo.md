# TODO list

* Look into semi-supervised approaches (start with [18] in 2018 paper)
* Look at {2,3}-Estimates
* Literature review

## Coding

### Admin
* Decide on coding style, and save config for pycodestyle/pylint
* Set up sphinx

### Implementation
* Allow different priors to be chosen for Sums and others
* Allow user to choose iteration modes:
  * (FIXED, n)
  * (CONVERGENCE, norm, delta)
* Decide what should happen if a source makes no claims (also if a varirable is
  not commented on by any sources)
  * Raise error?
  * Print warning?
  * Give 0/NaN/None trust/belief score?
