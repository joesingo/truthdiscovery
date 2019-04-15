# Introduction
* General
    * What truth discovery is
    * Applications of truth discovery
* Split rest into parts for practical and theoretical sides of the project

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

    * 'Data fusion' addresses the problem of combining data from multiple
      sources and resolving inconsistencies. Various approaches have been
      suggested (see review in Bleiholder, Naumann. Data Fusion): for example,
      taking the majority value, most recent value, or ignoring objects
      entirely where conflicts exist.

    * Problem with these approaches is that they do not consider the
      *trustworthiness* of the sources. One would expect that 'trustworthy'
      sources are more likely to provide true values than untrustworthy ones.
      If we have a method of determining source trust, this principle can be
      applied to accept claims that are *believable*, based on the
      trustworthiness of the sources purporting them.

    * For example, consider false information about a certain object that is
      shared amongst the public on social media, whilst a reputable news outlet
      publishes the true information. In this case the true information would
      be discarded if applying a majority vote, but trust-based analysis may
      (correctly) discard the false information.

* TD background:
    * *Truth discovery* has emerged as a topic aiming to tackle the problem of
      determining *what to believe* and *who to trust* given an input of
      conflicting claims from multiple sources.

    * TD methods often using the above principle, namely that believable claims are
      those made by trustworthy sources, and that trustworthy sources are those
      that make believable claims.

    * (reference TD surveys)

    * Prior to TD, there has been work on *trust analysis*, such as in P2P
      networks, sensor networks, e-commerce (eBay reputation etc), but these
      problems consider relations between a single type of entity
      (*homogeneous* in the terminology of Gupta and Han survey). For example,
      an agent in a multi-agent system may trust another agent.

    * However in truth discovery sources are not related to each other, and
      only interact indirectly through the claims they make

* Practical side:

    * Many truth discovery approaches and algorithms have been proposed in the
      literature. Different algorithms often use vastly different models,
      designed to address different (sometimes domain-specific) issues, such as
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

    * Due to the wide range of domains and variety in the approaches in the
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
  * Various TD approaches adopt statistical models to capture the
    trustworthiness of sources. This is treated as  random variable from a
    particular distribution ( *latent variables* ). TD then becomes a case of
    finding the most probable values for this variable, given the available
    evidence (i.e. the claims made by sources)

  * A common approach to this is *expectation maximisation* (see 'Latent
    Dirichlet Truth Discovery', 'A Truth Discovery Approach with Theoretical
    Guarantee', doubtless there are others too...)

  * This approach yields theoretical guarantees when if the underlying
    assumptions regarding the distribution of source trust/claimed values are
    satisfied. These assumptions may well hold in practise and give rise to
    useful algorithms

  *

  * TD is similar to many other areas in the literature…

* Break into practical and theoretical parts:;
    * Theoretical: Talk about related fields from a theoretical point of view
      (social choice, ranking etc). Give brief statement of the central
      problems in each related area, and explain how it relates to TD. Explain
      axiomatic method and how it has been applied in the related areas.

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

\end{itemize}

