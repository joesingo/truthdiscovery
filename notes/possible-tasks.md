* Implement some existing fact-finding algorithms from the literature, see,
  e.g., Section 3 from [1] or Section 4 from [2].

  (Note the most basic method is the “Hubs and Authorities” algorithm of
  Kleinberg, which is very closely related to PageRank, which I think it
  predates).

  [1]: https://pdfs.semanticscholar.org/579e/1e9217cfed6d563cedf8f8fdcd1604fc0917.pdf,
  [2]: http://www.vldb.org/pvldb/vol6/p97-li.pdf.

* Interesting special case will be binary variables

* Need to decide whether to just have binary claims or not

* Specify the variables and domains in advance
  * can be any number of variables, domains assumed to be finite initially?

* We need something that can load in any dataset
  * Form of dataset? csv file?
  * Maybe deduce the variables and domains automatically from the loaded
  dataset

* Also implement Hubs and Authorities and one or 2 others

* Include simple majority case for comparison

* Need to decide the language. Web-based?

* User should be able to enter the option for the prior.

* Form of the results:
  * Returns a table with all the belief and trust values?
  * Query-driven?
  * Possible queries?
  * Need to present trust values.

* After running, user should be prompted to provide additional cells in the
  table.

* Could apply to some interesting dataset from the web. Maybe something related
  to the “Fake News Challenge”? (http://www.fakenewschallenge.org/).

* Look into extending the methods so that they can be applied incrementally,
  i.e., look at the fluctuation of the output belief and trust values when
  sources provide their information gradually over time instead of all in one
  go.

* Come up with a couple of basic axioms (desirable properties) and compare a
  few of the existing algorithms with regard to whether they conform to the
  properties.

* Find a complete axiomatisation of the “Hubs and Authorities” algorithm, along
  the same lines as the one for PageRank.
