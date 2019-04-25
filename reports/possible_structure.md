# Introduction

* Brief intro to need for truth discovery
* Aims:
  * Produce easy to use software framework for running TD on real data,
    demonstration, and evaluation
  * Should be extendable framework to hopefully become a useful tool for
    researchers one the one hand to compare algorithms against each other,
    develop new algorithms, and analyse the behaviour of truth discovery, and
    as a tool in its own right to perform truth discovery on datasets of
    interest.
  * On the theoretical side, define a rigorous framework for truth discovery,
    highlighting parallels with other areas in the literature, especially voting
    theory in social choice.
* Audience:
  * Both practical and theoretical components will be of interest to
    researchers working in truth discovery
  * Practical part will also be useful for users wishing to perform analysis on
    their own datasets
* Scope:
  * Limited number of algorithms are implemented in this report (however the
    framework is easily extendible to many different algorithms)
  * Theoretical analysis is limited to one real-world algorithm, namely Sums
* Important outcomes:
  * Python library with web interface is produced
  * We develop a formal graph-theoretic framework, set the main problem of
    truth discovery in this framework, define a set of basic axioms
    (desirable properties) for truth discovery operators, and consider .

* (describe organisation of report)

# Background
* Motivation
    * Increasing amount of data available in today's world: can often find
      information about a given object from many different sources
    * Examples include information on the web, mobile sensing, social media
      data (e.g. Twitter data from users reporting on an event), scientific
      sensing
    * (Come up with examples for each of the above)

    * Data is available often in many different formats (web pages, natural
      language articles) and from disparate sources (news outlets, companies,
      members of the public, governmental organisations (find examples to back
      this up))

    * An inherent problem is that different sources provide *conflicting
      information* for an object.

    * This can be a result of:
        * deliberate misinformation: e.g. false information on the web (some
          stats on public trust in web data?)
        * out of date information
        * well-intentioned but unreliable sources
        * errors in information extraction (e.g. from natural language)

    * When considering data from sources with a priori unknown reliability, the
      questions becomes: which data do we accept as correct?

    * Simple methods such as majority voting (where the information claimed the
      most number of times is taken as correct) is prone to give poor results
      when sources are *not all equally trustworthy*.

    * For example, consider false information about a certain object that is
      shared widely amongst the public on social media, whilst a reputable news
      outlet publishes the true information. In this case the true information
      would be discarded if applying a majority vote.

    * The problem is that claims from a source carry as much weight as claims
      from any other. If trust were considered, we might find that the
      reputable news outlet is more trustworthy than the unknown social media
      users, and determine that their claims are the correct ones.

    * More generally, one would expect that trustworthy sources are more likely
      to provide true values than untrustworthy ones. If we have a method of
      determining source trust, this principle can be applied to accept claims
      that are *believable*, based on the trustworthiness of the sources
      purporting them.

    * *Truth discovery* has emerged as a topic aiming to tackle this problem of
      determining *what to believe* and *who to trust* given an input of
      conflicting claims from multiple sources.

    * TD methods often using the above principle, namely that believable claims
      are those made by trustworthy sources, and that trustworthy sources are
      those that make believable claims.

    * TD may also be applied for its own sake to calculate trustworthiness of
      sources

# Existing work
  * TD has two major components: determining *trust* and *belief* in sources
    and claims, and resolving conflicts in data. These two parts are tightly
    linked, since the trust evaluation is based on the claims in the input
    data, and which claims to accept is based on the trust evaluation.

  * Resolving conflicts in data:

  * 'Data fusion' addresses the problem of combining data from multiple
    sources and resolving inconsistencies. Various approaches have been
    suggested (see review in Bleiholder, Naumann. Data Fusion): for example,
    taking the majority value, most recent value, or ignoring objects
    entirely where conflicts exist.

  * 'Belief revision' concerns how to update a knowledge base upon receiving
    incompatible new information. It is formulated in a logical framework,
    where beliefs are propositional statements (in the basic form of belief
    revision at least...)

  * 'Abstract argumentation' considers which arguments to accept when given
    a network of conflicting arguments. The arguments considered here are
    left abstract: one only defines which arguments 'attack' each other,
    not what the arguments actually *are*.

  * Voting theory in social choice considers how to aggregate preferences
    from voters to form a social ranking, or selection of a single outcome.
    Voting rules aim to do this in a 'fair' way that reflects the will of
    the voters. The concept of fairness does not really apply here, but the
    task of aggregating conflicting information is still present.

  * Trust analysis:

  * (see 'Survey of Trust Models...' for references)

  * In the social sciences and economics: trust between humans has been
    considered for the effects on economic transactions (see [36-38] in
    'Survey of trust models'

  * Related, trust and reputation in e-commerce sites such as eBay

  * In sensor networks:
  * Collecting data from multiple sensor nodes, communicating over a
    potentially insecure channel (e.g. wirelessly). Nodes are required to
    report accurate data and behave cooperatively (e.g. for routing of
    packets through the network)

  * Nodes may misbehave as a result of system failure (e.g. hardware
    problems), or interference from an adversary.

  * Trust needs to be considered to mitigate the effects of such
    misbehaviour

  * Similar considerations for P2P networks, ad-hoc networks

  * Also some papers on trust-based belief revision, argumentation,
    recommendation, ranking (e.g. personalised ranking)

  * Loosely, ranking systems (e.g. PageRank) also employ this. A link from
    one page to another is seen as a sign of that page trusting the linked
    page as being an important page. Ranking systems use this structure to
    find the most 'important' pages.

  * From a theoretical view, see 'Formalising Trust as a Computational Concept'

  * The notion of trust in many of these approaches is *local*: it is the
    trust of one node in another, from that node's perspective.

  * It is is often based on the interactions or relations between entities,
    e.g. if A repeatedly provides accurate information to B, B may trust A.

  * In Gupta and Han this is called a *homogeneous network*, since the
    entities are of the same type.

  * This is not sufficient for the TD problem, where the sources do not
    interact directly and we aim to find a *global* measure of trust. Gupta
    and Han calls this a *hetrogeneous network*, where sources interact
    with other entities (facts, objects etc)

* TD approaches:
    * (reference TD surveys)

    * Many truth discovery approaches and algorithms have been proposed in the
      literature. Different algorithms often use vastly different models for
      the input and output, and the methods they employ:
      * Heuristics (Pasternack algorithms)
      * Probabilistic methods (TruthFinder, probably others...)
      * Optimisation methods (Conflicts to Harmony, probably others...)
      * Statistical methods (e.g. expectation maximisation: Latent Dirichlet,
        others...)

    * Additionally, different algorithms are designed to address different
      (sometimes domain-specific) issues, such as
        * implications between claims (TruthFinder)
        * hetrogeneous (multi-typed) data (conflicts to harmony)
        * object correlations (see 'A Probabilistic model for truth discovery
          with object correlations' and references therein)
        * hardness of facts (see Galland et. al.)
        * incorporating prior domain knowledge (Pasternack and Roth)
        * Trust- and untrust-worthy components of sources (see 'Latent
          Dirichlet Truth Discovery')
        * truth existence: true answers may not be present in data (see
          'Modelling Truth Existence in Truth Discovery)
        * sparsity (On Robust Truth Discovery in Sparse Social Media Sensing)
        * misinformation spread (On Robust Truth Discovery in Sparse Social
          Media Sensing)
        * semi-supervised (Semi-Supervised Truth Discovery)
        * copying between sources (Truth Discovery and Copying Detection...)
        * time-varying truth (Truth Discovery and Copying Detection...)
        * streaming data (Truth Discovery in Data Streams...)

* Background of practical software implementations:

    * Due to the wide range of domains and variety in the TD approaches in the
      literature, there is not likely to be a single algorithm that is best
      suited for all applications.

    * Instead, given a specific problem it may be necessary to try several
      approaches, or even tailor a bespoke algorithm, to achieve the best
      results (even evaluation of results is domain-specific: run time may be
      critical in some cases where accuracy is less important, whereas some
      domains may be insensitive to long run times but require precise
      accuracy)

    * For this reason there is a need for an extendible, well-documented,
      publicly-accessibly software framework for evaluation and comparison of
      truth discovery algorithms.

    * This will allow users to immediately try different algorithms on their
      data, and provide a framework for development of new algorithms that
      allows for easy comparison to existing methods

    * Existing solutions:
        * spectrum: https://github.com/totucuong/spectrum
            * This library implements some algorithms
            * It lacks proper documentation
            * Lacks features such as control of iteration, uniform interface
              for getting results, evaluation of algorithm accuracy on known
              datasets
        * DAFNA-EA: https://github.com/daqcri/DAFNA-EA
            * Fairly well-featured Java library
            * Web interfaces are available but not operational (as of 13th
              April 2019)
            * Java code is not documented, making extension difficult
            * Doesn't seem to provide methods of running algorithms on datasets
              other than when some ground truths are already known: i.e. it is
              purely for evaluation purposes rather than for actual
              applications of truth discovery
        * Other code is available on GitHub, but not suitable as a general
          purpose library
            * https://github.com/lvlingyu11/Truth-Discovery-for-Crowdsourcing-Data
            * https://github.com/MengtingWan/KDEm

    * Research questions:
      * Identify a common basic model for TD: in particular define format of
        input and output
      * Implement a basic selection well-known of TD algorithms
      * Find and implement standard metrics for evaluation of TD algorithms
      * Allow comparison between different algorithms
      * Produce well documented, tested, extendable software framework

* Theoretical:
  * Example of existing theoretical analysis: various TD approaches adopt
    statistical models to capture the trustworthiness of sources. This is
    treated as a random variable from a particular distribution ( *latent
    variables* ). TD then becomes a case of finding the most probable values
    for this variable, given the available evidence (i.e. the claims made by
    sources)

  * A common approach to this is *expectation maximisation* (see 'Latent
    Dirichlet Truth Discovery', 'A Truth Discovery Approach with Theoretical
    Guarantee', doubtless there are others too...)

  * This approach yields theoretical guarantees when if the underlying
    assumptions regarding the distribution of source trust/claimed values are
    satisfied. These assumptions may well hold in practise and give rise to
    useful algorithms

  * This kind of theoretical analysis only applies to *one algorithm at a
    time*. There is, as far as I am aware, no general theoretical framework for
    TD that goes beyond stating what the TD problem is, and allows multiple
    algorithms to be compared in it.

  * Doing so will allow TD to be related to other areas in the computer
    science/mathematical literature, understand TD more, prove results about TD
    algorithms that could guide algorithm development.

  * Other areas:
    * Voting in social choice
    * Judgment aggregation
    * Ranking systems
    * Recommendation systems
    * Argumentation

  * Give brief statement of the central problems in each related area, and
    explain how it relates to TD. Explain axiomatic method and how it has been
    applied in the related areas.

  * Research questions:

# Specification and Design/Approach

## Practical
* Practical: need to find common ground so that many algorithms from the
  literature can be implemented. Finding a common model for input/output means
  users can run multiple algorithms on the same data, without having to
  construct special datasets on a per algorithm basis

* Idea behind solution and design:
* Practical:
    * Goals: easy to use, well-documented, extendable, testable Python3 API and
      web-based interfaces
    * Architecture: class-based (create UML diagram). OO design makes it easy
      to develop and test to achieve extendability and testability
    * User-interface: For both API and web, interface is 'incremental': give
      basics (algorithm, dataset), and additional input is optional. For web,
      maybe talk about HCI concepts
    * Algorithms implemented

* High level requirements
  * As per the background to software implementations, there are specific use
    cases in mind for this implementation for different types of users
  * High-level overview of the types of users and activities they will be able
    to perform
  * These use cases can be represented visually with UML diagrams (talk about
    what UML is)
  * (show UML use case diagram)
  * Describe use cases in more detail
  * Notes on use cases:
    * Running algorithms on real truth discovery datasets
      * Load read-world datasets
        * Often large
        * Needs to be loaded from some suitable format
      * Get results in a suitable form
        * Raw trust and belief scores
        * Identified truth for each object
      * Evaluate performance of algorithms
        * Goal is to help determine which algorithm to use in practise
        * Accuracy on supervised data (see Pasternack and Roth, doubtless
          others too... Also relate to precision in data mining)
          * Supervised data could be real or synthetic
        * Time taken and asymptotic complexity
        * Convergence or otherwise
        * Memory usage and complexity
    * Algorithm development:
      * Infrastructure to write new algorithms without supporting framework
      * Evaluate performance
        * Goal is to compare to existing algorithms, or for empirical
          demonstration of theoretical properties (e.g. asymptotic complexity)
    * Tool for theoretical work:
      * Create simple examples and run algorithms
      * Produce diagrams
      * See the effect of changes in the input
      * Investigate axioms: empirical evidence of positive results, or
        production of counter examples

* Discuss user interfaces most suitable for different use cases
* Non-functional requirements such as testability, documentation, extendability

* ACTUAL STRUCTURE
* Identify different 'components' of the system
    * datasets
        * from CSV
        * from custom file format
        * from code
        * from graphical interface (website)
        * supervised data (from each of the above)
        * synthetic data
        * claim implications
    * algorithms
        * selection of algorithms
        * stopping criterion
        * parameters
        * talk about *extendability*
    * results and evaluation
        * accuracy on supervised data
        * time taken
        * memory usage
        * convergence speed
        * difference between results
        * user defined metrics
    * drawing
        * for creating examples visually
        * for visualising results for small datasets
        * animations: visualise convergence in addition to static behaviour
* Briefly discuss each one
* Will also discuss non-functional requirements
    * testing
    * documentation
    * extendability
    * simplicity
    * performance
* Dataset, algorithm and results requirements depend on the model adopted. Have
  section explaining model choice
* More detailed section on each component + non-functional requirements
    * Discussion
    * List of requirements
* Describe user interfaces
    * Consider user types
    * Different goals for different user interfaces
    * List of requirements

* DESIGN
* UML class diagram
* Sequence or activity diagram for web interface? (only part complicated enough
  to warrant it?)

## Theoretical

* Have mentioned in background section that a general framework for truth
  discovery is sought after. To work towards this, we need to set out exactly
  what this 'framework' will entail, and what requirements it ought to satisfy.

* The main goal is to set out rigorous definitions for what truth discovery
  is, which allows the current situation to be modelled. This includes:

  * What is the 'input' to truth discovery? We have described the input in
    terms of sources, facts, objects and conflicting claims, but this needs to
    be formalised mathematically.

  * What is the output? We have stated that the output is trust and belief
    scores for sources and facts, according to the most common approach taken
    in the literature. However our aims are to study truth discovery in full
    generality, not just the algorithms already in existence. Therefore a more
    general view could be taken, so long as it can still model existing
    algorithms.

* With these ideas formalised, a truth discovery algorithm is simply a mapping
  from the space of inputs to outputs. This abstracts away the *process* of
  performing truth discovery so that 'algorithm' is not the correct term to
  use. We opt for *truth discovery operator* to describe a mapping from inputs
  to outputs.

* There are several criteria against which to judge the usefulness of the
  developed framework:
  * Ability to model existing approaches. We aim to find a unified framework to
    allow as many algorithms in the literature to be compared with one another.

  * Simplicity of the formulation: it should be easy to understand and easy to
    relate to intuitive notions of truth discovery

  * Flexibility: we wish to prove properties of operators, compare different
    operators, and develop axioms, so the framework should be easy to work in

  * Generality: needs to be general enough to support future work. Should also
    be unopinionated, so as to be useful as a foundational theory rather than
    an implementation of a specific approach. It should also be general in
    order to be compared to other areas in the literature in a simple way. This
    allows ideas from these areas to be applied to truth discovery, e.g. many
    axioms from social choice have a counterpart in truth discovery.

* Once the framework has been established, we aim to develop axioms for
  operators. In line with axiomatic foundations for other problems, the axioms
  should represent intuitively desirable properties that a 'reasonable'
  operator should satisfy. The power of the axiomatic approach is to consider
  multiple axioms together; the types of results attained include
  *impossibility results*, where it is proved that no algorithm\footnotemark
  can satisfy a set of axioms, and *representation theorems*, where a set of
  sound and complete axioms are found for a particular algorithm. For example,
  in Altman ranking the authors show that two seemingly complementary axioms
  are in fact contradictory, which has implications when deciding which ranking
  system to use in practise.

* \footnotetext{We write algorithm as a blanket term to refer to social choice
functions, ranking systems, annotation aggregators etc}

* Requirements for axioms are therefore that they have simple interpretations,
  are desirable properties in some way or another, and that they can be
  considered in conjunction.

### Existing formalisms

* We start by reviewing the formalisms present in some popular approaches in
  the truth discovery literature, and then in related areas already having
  foundational frameworks and which the axiomatic method is well established.
  This will provide useful context for developing a theory meeting the aims
  described above.

* (go through background notes, and for input and output, *roughly* explain the
  existing formulations. Also explain how there are mostly compatible with each
  other)

* (go through social choice, judgment aggregation, ranking systems (+ personal
  ranking systems), collective annotation. again, roughly explain the ideas)

### Approach taken

* This background allows us to make informed choices as to how to develop a
  formal framework

* For input, we choose a graph-theoretic representation
  * Simple to interpret
  * Concepts in graph theory can be usefully applied to describe properties of
    the input network (e.g. connected component for independence axiom)
  * Provides flexibility for future refinements: e.g. one may consider weighted
    edges, annotated nodes etc to conveniently encode additional information
    about the input data
  * Also makes explicit the connection of truth discovery with ranking systems;
    indeed, truth discovery can be seen as a sort of ranking on a bipartite
    graph where only a subset of the nodes (the facts) are ranked
  * Existing formalisms in truth discovery literature can be simply represented
    as graphs

* For output, the situation is more nuanced, as there are different forms of
  output for different algorithms

* Different approaches are largely in agreement with regards to the treatment
  of sources: each source is assigned a *trust score* (usually a number in $[0,
  1]$). Differences appear for the treatment of facts; the two main approaches
  are to assign each fact a belief score, or to select a single 'true' fact for
  each object.

* Clearly the former approach provides more information; adopting the latter
  for a general theory would unnecessarily ignore this extra information for a
  large number of real-world algorithms.

* Also, the latter can be seen as a special case of the former, where the
  selected true facts receive scores of 1 and all others receive 0.

* One may note that assigning a numeric score to each source and fact in
  particular induces an *ordering* of the sources and facts. We argue that the
  essence of truth discovery lies more in this induced ordering that the
  particular numerical scores. Indeed, in applications of truth discovery for
  finding true facts, one will often take the fact with highest score as the
  true fact for a given object, i.e. the maximum element with respect to the
  induced ordering on the set of facts for the object.

* A similar view is taken in social choice (Arrow) and ranking systems (Altman
  ranking, Altman PageRank). Taking the same approach also makes our framework
  more easily comparable with these areas, and allows useful concepts to be
  translated to truth discovery

* Nevertheless, to model in their entirety the algorithms that produce numeric
  scores, it will be possible to define such operators in the framework as more
  general objects, but restrict our attention mainly to the ranking-output
  operators.

# Implementation
# Results and Evaluation

* Theoretical work:
  * Discuss suitability along the criteria mentioned in approach section

  * Ability to model existing approaches:
    * As seen at the end of the section, Sums was defined in the framework as
      an iterative operator. Due to time constraints, no other algorithms were
      formally defined.

    * However, the definition of an iterative operator is sufficient to cover
      many more algorithms. This is immediately clear for algorithm very
      similar to sums, such as Average.Log, Investment and PooledInvestment,
      since the only difference in their definitions is the expression for the
      recursive trust and belief update; their fundamental method of operation
      is the same.

    * Sums and its related algorithms are particularly easy to realise in the
      framework since their output (trust and belief scores for each source and
      fact) is the same as the output of a *numeric operator*

    * That is not to say that other algorithm that do not operate in this way
      cannot be modelled. For example, any algorithm which outputs an
      identified true fact for an object can be considered as a numeric
      iterative operator which assigns the identified truths a score of 1, and
      all other facts 0.

    * A more extreme case is where an algorithm predicts the true fact for an
      object as one which was not proposed by any source (conflicts to
      harmony). Fortunately this is not a problem in the framework, due to the
      fact that we allow no-source facts to be present in a network. One may
      simply take the set of facts for an object to be *all* permitted values
      for the object (we make the assumption that the domain of possible values
      is well-defined as a set)

  * Simplicity
    * This is naturally a subjective aim, and what appears simple to the author
      may well not appear simple to others.

    * Nonetheless, we argue that the framework achieves its aim of expressing
      ideas as simply as possible

    * For example, one of the key definitions is that of truth discovery
      network. Adopting a graph-theoretic approach, the definition (including
      the constraints on the graph) is easy to understand for those familiar
      with the basics of graphs, and even lends itself to pictorial
      representations of truth discovery networks.

    * The next main definition is that of a truth discovery operator. This is
      defined simply as a mapping from a space of inputs ($\N$) to a space of
      outputs (pairs of rankings of sources and facts: $\orderings(\S) \times
      \ordering(\F)$.

    * Whilst the notation for the rankings for a particular operator and
      particular network may appear crowded at first, it expresses all the
      components of the ranking without having to introduce additional notation
      prior to its use each time (it is inspired by the notation used by Altman
      and Tennenholtz (foundations))

    * The definition of an iterative operator extends the non-iterative one in
      a natural way, by defining it simply as a sequence of non-iterative
      operators

    * We also believe that the axioms are expressed as simply as possible.
      Where the formalities become tedious, plain-English explanations are
      provided to give insight into the definitions.

  * Flexibility:
    * Again, this cannot be objectively verified. Nevertheless, many different
      ideas were expressed in the framework, and the basic results shown have
      relatively simple proofs.

  * Generality:
    * By and large, the framework is neutral with respect to any specific idea
      or approach for truth discovery. An exception is perhaps the definition
      of an iterative operator, which uses the numeric-score approach, which
      not all iterative algorithms in practise do. As mentioned above, this
      does not *prevent* such algorithms being represented, but it does hurt
      the generality of the framework. The definition could instead be more
      general and be a sequence of non-numeric operators. The definition as it
      stands was chosen to improve the flow of the work, since the only
      iterative algorithm actually discussed does in fact use numeric scores.

    * Another desirable aspect of the framework is to permit comparison between
      truth discovery and related areas in the literature. Whilst clearly being
      an theory of truth discovery, the framework is general enough for this;
      one may easily see truth discovery networks and operators from the
      perspective of social choice and ranking systems. For example, it is
      easily seen that truth discovery networks are a particular class of
      graphs, and a truth discovery operator is essentially a pair of ranking
      systems that rank the sources and facts. The similarity is also
      demonstrated empirically by the fact that many of the developed axioms
      are directly inspired by axioms in these areas, but still have intuitive
      interpretations in terms of truth discovery.

  * Besides the framework itself, should evaluate the work done inside it
    * Axioms
      * Several axioms with intuitive backing, which cover a wide range of
        ideas
      * Little work on the interplay between axioms
    * Analysis of operators wrt axioms
      * Very simple representation theorem is given: symmetry and dictatorship
        leads to the trivial ranking of sources
      * Sound axioms were found for Sums, but these are not complete
      * No impossibility results
      * No comparison *between algorithms*. For example, one could find axioms
        that distinguish between different algorithms. This could provide
        insight into the meaningful differences between algorithms, which is
        hard to obtain from the definitions in terms of trust and belief scores
        -- especially since the final ranking depends on the convergence of
        these mutually dependent scores
    * Comparison to other areas
      * Similarities can be seen at a basic level, in particular with social
        choice (sources are voters, facts are alternatives, and sources rank
        their claimed facts above all others) and ranking systems
      * No real work has been done on similarities with other areas
      * For example, could formulate social welfare functions or ranking
        systems as truth discovery operators and vice versa
      * Comparison is limited to social choice and derived areas: the
        similarities with argumentation theory and belief revision are less
        clear

# Future work

