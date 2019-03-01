06-02-2019:
-----------
* Finished off supervised and synthetic dataset creation
* Created test script to compare basic algorithms on synthetic datasets

07-02-2019:
-----------
* Read some papers and make notes
* Fixed synthetic data creation to ensure that all variables are claimed on,
  and all sources make at least one claim
* Start implementing PooledInvestment

08-02-2019:
-----------
* Finish PooledInvestment
* Add regression tests for output of algorithms on a fixed dataset
* Load supervised datasets from CSV

09-02-2019:
-----------
* Start some documentation in README

10-02-2019:
-----------
* Add dataset that can store implications between claims, for TruthFinder
* Implement TruthFinder

12-02-2019:
-----------
* Read Semi-Supervised Truth-Discovery paper
* Write sample script to play around with running algorithms
* *MEETING*

13-02-2019:
-----------
* Add tests for code style
* Refactor supervised dataset class

14-02-2019:
-----------
* Allow algorithms to run till convergence, or use a fixed number of iterations
* Make a start on documentation

15-02-2019:
-----------
* Export synthetic data to CSV

16-02-2019:
-----------
* Debug and attempt to fix issues with TruthFinder

17-02-2019:
-----------
* Work on running algorithms with real-world data
* Big refactor of Dataset and related classes, to allow text data

18-02-2019:
-----------
* Continuing refactoring work

19-02-2019:
-----------
* Finish refactor and update documentation and tests
* *MEETING*

20-02-2019:
-----------
* Prevent division by zero errors

[21-25]-02-2019:
----------------
* Background reading on truth-discovery approaches, to find common framework
  for developing axioms
* Sketch possible formalisms of truth-discovery
* Research existing work on axioms of ranking systems
* Come up with a few basic ideas for axioms, which are not fully detailed yet

26-02-2019:
-----------
* *MEETING*
* Return time taken for algorithms to run
* Add example script for running algorithms on different sizes datasets,
  recording the run time, and plotting results on a graph
* Tidy up notes on potential formal definitions, following feedback

27-02-2019:
-----------
* Investigate returning memory usage of algorithms
* Add more to documentation for giving input

28-02-2019:
-----------
* Try algorithms on real-world stock data
* Investigate using sparse matrices
* Read about judgement aggregation, collective annotation, social choice
* Try to formulate symmetry axiom for my truth-discovery framework
