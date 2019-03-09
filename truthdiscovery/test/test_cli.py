import numpy.ma as ma
import pytest
import yaml

from truthdiscovery.algorithm import AverageLog, Sums, TruthFinder, PriorBelief
from truthdiscovery.client.cli import CommandLineClient
from truthdiscovery.input import MatrixDataset
from truthdiscovery.utils import (
    ConvergenceIterator,
    DistanceMeasures,
    FixedIterator
)


class TestCommandLineClient:
    def run(self, *args):
        CommandLineClient.run(args)

    def get_parsed_args(self, *args):
        return CommandLineClient.get_parser().parse_args(args)

    @pytest.fixture
    def csv_dataset(self, tmpdir):
        csvfile = tmpdir.join("data.csv")
        dataset = MatrixDataset(ma.masked_values([
            [1, 2, 3, 0],
            [3, 0, 1, 2],
            [2, 2, 0, 0],
            [0, 1, 0, 3]
        ], 0))
        csvfile.write(dataset.to_csv())
        return str(csvfile)

    def test_basic(self, csv_dataset):
        self.run(
            "run", "--algorithm", "sums", "-f", csv_dataset
        )

    def test_results(self, csv_dataset, capsys):
        self.run(
            "run", "-a", "average_log", "-f", csv_dataset
        )
        got_results = yaml.load(capsys.readouterr().out)
        exp_results = AverageLog().run(MatrixDataset.from_csv(csv_dataset))
        assert got_results["trust"] == exp_results.trust
        assert got_results["belief"] == exp_results.belief
        assert got_results["iterations"] == exp_results.iterations

    def test_get_algorithm_instance(self, csv_dataset):
        args = self.get_parsed_args(
            "run", "--algorithm", "truthfinder", "-p", "dampening_factor=0.1",
            "-p", "influence_param=0.77", "-f", csv_dataset
        )
        alg = CommandLineClient.get_algorithm_object(args)
        assert isinstance(alg, TruthFinder)
        assert alg.dampening_factor == 0.1
        assert alg.influence_param == 0.77

    def test_set_prior_belief(self, csv_dataset, capsys):
        args = self.get_parsed_args(
            "run", "--algorithm", "sums", "-p", "priors=voted", "-f",
            csv_dataset
        )
        alg = CommandLineClient.get_algorithm_object(args)
        assert isinstance(alg, Sums)
        assert alg.priors == PriorBelief.VOTED

        # Invalid prior string
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "sums", "-p", "priors=blah", "-f",
                csv_dataset
            )

        err_msg = capsys.readouterr().err
        assert "invalid algorithm_parameter" in err_msg
        assert "priors=blah" in err_msg

    def test_set_iterator(self, csv_dataset, capsys):
        # Fixed iterator
        args1 = self.get_parsed_args(
            "run", "--algorithm", "sums", "-p", "iterator=fixed-123", "-f",
            csv_dataset
        )
        alg1 = CommandLineClient.get_algorithm_object(args1)
        assert isinstance(alg1, Sums)
        assert isinstance(alg1.iterator, FixedIterator)
        assert alg1.iterator.limit == 123

        # Convergence iterator
        args2 = self.get_parsed_args(
            "run", "--algorithm", "sums", "-p",
            "iterator=cosine-convergence-0.01", "-f", csv_dataset
        )
        alg2 = CommandLineClient.get_algorithm_object(args2)
        assert isinstance(alg2.iterator, ConvergenceIterator)
        assert alg2.iterator.distance_measure == DistanceMeasures.COSINE
        assert alg2.iterator.threshold == 0.01

        # Convergence iterator with limit
        args3 = self.get_parsed_args(
            "run", "--algorithm", "sums", "-p",
            "iterator=l2-convergence-0.3-limit-99", "-f", csv_dataset
        )
        alg3 = CommandLineClient.get_algorithm_object(args3)
        assert isinstance(alg3.iterator, ConvergenceIterator)
        assert alg3.iterator.distance_measure == DistanceMeasures.L2
        assert alg3.iterator.threshold == 0.3
        assert alg3.iterator.limit == 99

        # Convergence iterator with invalid distance measure
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "sums", "-p",
                "iterator=blah-convergence-0.3-limit-99", "-f", csv_dataset
            )
        assert "invalid distance measure 'blah'" in capsys.readouterr().err

        # Invalid iterator specification
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "sums", "-p",
                "iterator=hello", "-f", csv_dataset
            )
        assert "invalid iterator specification" in capsys.readouterr().err

    def test_invalid_algorithm_parameter(self, csv_dataset, capsys):
        # Invalid name
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "truthfinder", "-p", "myextraparm=0.1",
                "-f", csv_dataset
            )
        err = capsys.readouterr().err
        assert "invalid parameter" in err
        assert "myextraparm" in err

        # Invalid format
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "truthfinder", "-p", "initial_trust 0.1",
                "-f", csv_dataset
            )
        assert "must be in the form 'key=value'" in capsys.readouterr().err

    def test_invalid_algorithm(self, csv_dataset, capsys):
        with pytest.raises(SystemExit):
            self.run(
                "run", "--algorithm", "joesalgorithm", "-f", csv_dataset
            )
        assert (
            "invalid algorithm label 'joesalgorithm'"
            in capsys.readouterr().err
        )
