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

# Approach
* Numerous models of TD in the literature. Practical and theoretical sides have
  different goals and requirements for a model
* Theoretical: At least two aspects to consider
    * How to develop a useful formal framework compatible with existing
      formalisations for related problems. This allows easy comparison (e.g to
      see that TD is special case of voting, and easily compared with
      collective annotation), and results from other areas can be translated to
      TD (e.g. most social choice concepts)
    * How to develop framework applicable to real world use cases and existing
      algorithms (e.g. to compare real-world algorithms w.r.t their theoretical
      properties). Such frameworks are provided in all TD literature, but are
      not always compatible
    * These are distinct goals: a framework easily comparable to voting theory,
      say, may not represent real TD accurately
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
* Theoretical:
    * Aim to find formal framework to analyse TD and TD algorithms, and to
      explore axioms
    * Approach: study existing formalisations of similar subject areas in the
      literature

# Implementation
# Results and Evaluation

# Future work

* Theoretical work:
  * General:
    * Approach has been to follow social choice and closely related literature

    * Could instead look to other areas like argumentation and data mining
    literature (?)

  * Framework limitations:
    * Some real-world algorithms only give most believed values as output
      (neither a ranking nor belief score for each fact) (e.g.  'Conflicts to
      Harmony'). However we *can* view such an operator in the framework by
      considering it to rank the discovered true facts above all others, and
      ranking false facts equally.

    * Some algorithms give most-believed values for facts that are *not claimed
    by any sources*, e.g. if values are continuous could perform a weighted
    average of claimed facts (I believe this is done in 'Conflicts to
    Harmony' for continuous data types). Neither of the operator definitions
    in the theory support this.

    * Objects do not really play a role for most of the work. Maybe they could
    be removed from the framework if they do not play a significant role, or
    more work could be done to actually use the concept of objects.

  * Potential framework extensions:
    * Support the numerous extensions to basic TD

    * There is a lot of redundancy in the axioms where we state a property that
      the source ranking should have, and an almost identical version for fact
      ranking. Similarly in the proofs, it is often the case that the argument
      for facts is identical to the one for sources.

    * Perhaps there is a more general problem or framework, where we have k
    groups of nodes instead of just 2 (sources and facts). The interpretation
    of such a network would need considering.

    * Maybe the stuff in Pasternack's thesis on 'groups' is relevant to this
