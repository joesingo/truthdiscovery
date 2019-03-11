"""
Command-line interface to truthdiscovery library
"""
import argparse
from enum import Enum
import re
import sys

import numpy as np
import yaml

from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    PriorBelief,
    Sums,
    TruthFinder
)
from truthdiscovery.input import MatrixDataset, SupervisedData, SyntheticData
from truthdiscovery.utils import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator
)


def numpy_float_yaml_representer(dumper, val):
    """
    Convert numpy float64 objects to Python floats for YAML representation
    """
    return dumper.represent_float(float(val))


yaml.add_representer(np.float64, numpy_float_yaml_representer)


class OutputFields(Enum):
    ACCURACY = "accuracy"
    BELIEF = "belief"
    BELIEF_STATS = "belief-stats"
    ITERATIONS = "iterations"
    MOST_BELIEVED = "most-believed-values"
    TIME = "time"
    TRUST = "trust"
    TRUST_STATS = "trust-stats"


class CommandLineClient:
    ALG_LABEL_MAPPING = {
        "average_log": AverageLog,
        "investment": Investment,
        "pooled_investment": PooledInvestment,
        "sums": Sums,
        "truthfinder": TruthFinder,
        "voting": MajorityVoting
    }

    @staticmethod
    def get_parser():
        """
        :return: argparse ArgumentParser object
        """
        parser = argparse.ArgumentParser(description=__doc__)
        subparsers = parser.add_subparsers(
            dest="command",
            metavar="COMMAND",
        )
        # Run sub-command
        run_parser = subparsers.add_parser(
            "run",
            help="Run a truth-discovery algorithm on a CSV dataset",
            description="""
                Run an algorithm on a dataset loaded from a CSV file, and
                return results in YAML format
            """,
        )
        run_parser.add_argument(
            "-a", "--algorithm",
            help="The algorithm to run: choose from {}".format(
                ", ".join(CommandLineClient.ALG_LABEL_MAPPING.keys())
            ),
            required=True,
            dest="alg_cls",
            metavar="ALGORITHM",
            type=CommandLineClient.algorithm_cls,
        )
        run_parser.add_argument(
            "-p", "--params",
            help=("""
                Parameters to pass to the algorithm, each in the form
                'key=value'. For 'priors', see the PriorBelief enumeration for
                valid values. For 'iterator', use the format 'fixed-<N>' for
                fixed N iterations, or
                '<measure>-convergence-<threshold>[-limit-<N>]' for convergence
                in 'measure' within 'threshold', up to an optional maximum
                number 'limit' iterations.
            """),
            dest="alg_params",
            metavar="PARAM",
            type=CommandLineClient.algorithm_parameter,
            nargs="+",
        )
        run_parser.add_argument(
            "-f", "--dataset",
            help="CSV file to run the algorithm on",
            required=True
        )
        run_parser.add_argument(
            "-s", "--supervised",
            help=("Interpret the CSV as a supervised dataset, i.e. treat the "
                  "first row as known true values"),
            action="store_true",
            dest="supervised"
        )
        # Output options
        output_group = run_parser.add_argument_group(
            title="output options",
            description="options for controlling what output is given"
        )
        output_group.add_argument(
            "--sources",
            help=("Sources to restrict results to. Unknown sources are "
                  "ignored"),
            dest="sources",
            metavar="SOURCE",
            nargs="+",
            type=int
        )
        output_group.add_argument(
            "--variables",
            help=("Variables to restrict results to. Unknown variables are "
                  "ignored"),
            dest="variables",
            metavar="VAR",
            nargs="+",
            type=int
        )
        output_field_choices = [f.value for f in OutputFields]
        output_group.add_argument(
            "-o", "--output",
            help=(
                "Fields to include in the output: choose from {}"
                .format(", ".join(output_field_choices))
            ),
            metavar="OUTPUT_FIELD",
            dest="output_fields",
            nargs="+",
            type=OutputFields,
            default=[
                OutputFields.TRUST, OutputFields.BELIEF,
                OutputFields.ITERATIONS, OutputFields.TIME
            ]
        )

        # Synthetic data generation sub-command
        synth_parser = subparsers.add_parser(
            "synth",
            help="Generate a synthetic CSV dataset",
            description="""
                Randomly generate a CSV dataset based on a given list of source
                trust scores, which are interpreted as the probability that
                each source makes a correct claim. The first row in the output
                gives the true values, and the subsequent rows are the source
                claims.
            """
        )
        synth_parser.add_argument(
            "--trust",
            help="Trust scores for sources in [0, 1]",
            metavar="TRUST_SCORE",
            nargs="+",
            required=True,
            type=float
        )
        synth_parser.add_argument(
            "--num-vars",
            help="The number of variables to generate",
            metavar="NUM_VARS",
            type=int
        )
        synth_parser.add_argument(
            "--claim-prob",
            help=("The probability that a given source will make a claim for "
                  "a given variable"),
            metavar="CLAIM_PROB",
            type=float
        )
        synth_parser.add_argument(
            "--domain-size",
            help="The number of possible values for each variable",
            metavar="DOMAIN_SIZE",
            type=int
        )
        return parser

    @staticmethod
    def algorithm_cls(alg_label):
        """
        Function used as argparse type for algorithm class

        :param alg_label: string label for an algorithm
        :return: the algorithm class corresponding to the given label
        """
        try:
            return CommandLineClient.ALG_LABEL_MAPPING[alg_label]
        except KeyError:
            raise argparse.ArgumentTypeError(
                "invalid algorithm label '{}'".format(alg_label)
            )

    @staticmethod
    def algorithm_parameter(param_string):
        """
        Function used as argparse type for parameters

        :param: string from command-line arguments
        :return: a pair ``(param_name, value)``
        """
        try:
            param, value = map(str.strip, param_string.split("=", maxsplit=1))
        except ValueError:
            raise argparse.ArgumentTypeError(
                "parameters must be in the form 'key=value'"
            )
        # Map param name to a callable to convert string to correct type
        type_mapping = {
            "iterator": CommandLineClient.get_iterator,
            "priors": PriorBelief
        }
        type_convertor = type_mapping.get(param, float)
        return (param, type_convertor(value))

    @staticmethod
    def get_iterator(it_string):
        """
        Parse an :any:`Iterator` object from a string description
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
                raise argparse.ArgumentTypeError(
                    "invalid distance measure '{}'".format(measure_str)
                )
            threshold = float(convergence_match.group("threshold"))
            limit = None
            if convergence_match.group("limit") is not None:
                limit = int(convergence_match.group("limit"))
            return ConvergenceIterator(measure, threshold, limit)

        raise argparse.ArgumentTypeError(
            "invalid iterator specification '{}'".format(it_string)
        )

    @staticmethod
    def get_algorithm_object(parsed_args):
        """
        Process the parsed command-line arguments and return the algorithm
        instance to use
        """
        cls = parsed_args.alg_cls
        params = dict(parsed_args.alg_params or [])
        try:
            return cls(**params)
        except TypeError:
            raise ValueError(
                "invalid parameters {} for {}".format(params, cls.__name__)
            )

    @staticmethod
    def run(cli_args):
        parser = CommandLineClient.get_parser()
        args = parser.parse_args(cli_args)

        if args.command == "run":
            CommandLineClient.run_algorithm(args, parser)
        elif args.command == "synth":
            CommandLineClient.generate_synthetic(args, parser)
        else:
            parser.print_help()

    @staticmethod
    def run_algorithm(args, parser):
        try:
            alg_obj = CommandLineClient.get_algorithm_object(args)
        except ValueError as ex:
            parser.error(ex)

        sup_data = None
        dataset = None
        if args.supervised:
            sup_data = SupervisedData.from_csv(args.dataset)
            dataset = sup_data.data
        else:
            # Catch error early if accuracy requested in output but dataset is
            # not supervised
            if OutputFields.ACCURACY in args.output_fields:
                parser.error("cannot calculate accuracy without --supervised")
            dataset = MatrixDataset.from_csv(args.dataset)

        results = alg_obj.run(dataset).filter(sources=args.sources,
                                              variables=args.variables)

        # Get results to display
        display_results = {}
        if OutputFields.TIME in args.output_fields:
            display_results["time_taken"] = results.time_taken

        if OutputFields.ITERATIONS in args.output_fields:
            display_results["iterations"] = results.iterations

        if OutputFields.TRUST in args.output_fields:
            display_results["trust"] = results.trust

        if OutputFields.BELIEF in args.output_fields:
            display_results["belief"] = results.belief

        if OutputFields.TRUST_STATS in args.output_fields:
            mean, stddev = results.get_trust_stats()
            display_results["trust_stats"] = {"mean": mean, "stddev": stddev}

        if OutputFields.BELIEF_STATS in args.output_fields:
            belief_stats = results.get_belief_stats()
            display_results["belief_stats"] = {
                var: {"mean": mean, "stddev": stddev}
                for var, (mean, stddev) in belief_stats.items()
            }

        if OutputFields.ACCURACY in args.output_fields:
            try:
                acc = sup_data.get_accuracy(results)
            except ValueError:
                acc = None
            display_results["accuracy"] = acc

        if OutputFields.MOST_BELIEVED in args.output_fields:
            most_bel = {}
            for var in results.belief:
                most_bel[var] = sorted(results.get_most_believed_values(var))
            display_results["most_believed_values"] = most_bel

        print(yaml.dump(display_results, indent=2, default_flow_style=False))

    @staticmethod
    def generate_synthetic(args, parser):
        kwargs = {
            "trust": args.trust,
            "num_variables": args.num_vars,
            "claim_probability": args.claim_prob,
            "domain_size": args.domain_size
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        try:
            print(SyntheticData(**kwargs).to_csv())
        except ValueError as ex:
            parser.error(ex)


def main():  # pragma: no cover
    CommandLineClient.run(sys.argv[1:])
