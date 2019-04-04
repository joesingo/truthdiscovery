from enum import Enum
import re

from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    PriorBelief,
    Sums,
    TruthFinder
)
from truthdiscovery.utils import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator
)


class OutputFields(Enum):
    """
    Fields available to show in results to a user
    """
    ACCURACY = "accuracy"
    BELIEF = "belief"
    BELIEF_STATS = "belief_stats"
    ITERATIONS = "iterations"
    MOST_BELIEVED = "most_believed_values"
    TIME = "time"
    TRUST = "trust"
    TRUST_STATS = "trust_stats"


class BaseClient:
    """
    Base class to provide functionality common to any interface to the library
    """
    ALG_LABEL_MAPPING = {
        "average_log": AverageLog,
        "investment": Investment,
        "pooled_investment": PooledInvestment,
        "sums": Sums,
        "truthfinder": TruthFinder,
        "voting": MajorityVoting
    }

    def algorithm_cls(self, alg_label):
        """
        Return the algorithm class corresponding to a string label
        """
        try:
            return self.ALG_LABEL_MAPPING[alg_label]
        except KeyError:
            raise ValueError(
                "invalid algorithm label '{}'".format(alg_label)
            )

    def algorithm_parameter(self, param_string):
        """
        Parse a string representation of a parameter to construct an algorithm
        object with

        :return: a pair ``(param_name, value)``
        """
        try:
            param, value = map(str.strip, param_string.split("=", maxsplit=1))
        except ValueError:
            raise ValueError(
                "parameters must be in the form 'key=value'"
            )
        # Map param name to a callable to convert string to correct type
        type_mapping = {
            "iterator": self.get_iterator,
            "priors": PriorBelief
        }
        type_convertor = type_mapping.get(param, float)
        return (param, type_convertor(value))

    def get_iterator(self, it_string):
        """
        Parse an :any:`Iterator` object from a string representation
        """
        fixed_regex = re.compile(r"fixed-(?P<limit>\d+)$")
        convergence_regex = re.compile(
            r"(?P<measure>[^-]+)-convergence-(?P<threshold>[^-]+)"
            r"(-limit-(?P<limit>\d+))?$"  # optional limit
        )
        fixed_match = fixed_regex.match(it_string)
        if fixed_match:
            return FixedIterator(limit=int(fixed_match.group("limit")))

        convergence_match = convergence_regex.match(it_string)
        if convergence_match:
            measure_str = convergence_match.group("measure")
            try:
                measure = DistanceMeasures(measure_str)
            except ValueError:
                raise ValueError(
                    "invalid distance measure '{}'".format(measure_str)
                )
            threshold = float(convergence_match.group("threshold"))
            limit = None
            if convergence_match.group("limit") is not None:
                limit = int(convergence_match.group("limit"))
            return ConvergenceIterator(measure, threshold, limit)

        raise ValueError(
            "invalid iterator specification '{}'".format(it_string)
        )

    def get_algorithm_object(self, alg_cls, param_dict):
        """
        Instantiate an algorithm object

        :raises ValueError: if parameters are invalid
        """
        try:
            return alg_cls(**param_dict)
        except TypeError:
            raise ValueError(
                "invalid parameters for {}".format(alg_cls.__name__)
            )

    def get_output_obj(self, results, output_fields=None, sup_data=None):
        """
        Format a :any:`Result` class as a dictionary to present as output to
        the user. If ``output_fields`` is None, include all available fields
        """
        output_fields = output_fields or list(OutputFields)
        out = {}

        for field in output_fields:
            if field == OutputFields.TIME:
                out[field.value] = results.time_taken

            if field == OutputFields.ITERATIONS:
                out[field.value] = results.iterations

            if field == OutputFields.TRUST:
                out[field.value] = results.trust

            if field == OutputFields.BELIEF:
                out[field.value] = results.belief

            if field == OutputFields.TRUST_STATS:
                mean, stddev = results.get_trust_stats()
                out[field.value] = {"mean": mean, "stddev": stddev}

            if field == OutputFields.BELIEF_STATS:
                belief_stats = results.get_belief_stats()
                out[field.value] = {
                    var: {"mean": mean, "stddev": stddev}
                    for var, (mean, stddev) in belief_stats.items()
                }

            if sup_data is not None and field == OutputFields.ACCURACY:
                try:
                    acc = sup_data.get_accuracy(results)
                except ValueError:
                    acc = None
                out[field.value] = acc

            if field == OutputFields.MOST_BELIEVED:
                most_bel = {}
                for var in results.belief:
                    most_bel[var] = sorted(
                        results.get_most_believed_values(var)
                    )
                out[field.value] = most_bel

        return out
