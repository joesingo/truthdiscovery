"""
Script to load a real-world dataset of stock market data, and perform
truth-discovery.
"""
import csv
import sys
import time

from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    Sums,
    TruthFinder
)
from truthdiscovery.input import FileDataset, FileSupervisedData


class StockBase:
    """
    Base class to provide functions required for parsing both data and truth
    files
    """
    def get_tsv_reader(self, fileobj):
        return csv.reader(fileobj, delimiter="\t")

    def get_variable_name(self, symbol, date, attr_index):
        return "{}_{}_attr_{}".format(symbol, date, attr_index)

    def clean_value(self, value):
        bad_chars = ("$", "%", "+", "-")
        for char in bad_chars:
            value = value.replace(char, "")
        return value.strip()

    def get_var_vals(self, row, date):
        """
        Yield tuples of the form (var, val) for each value in the given row.
        Note that ``row`` should not include the source or date.
        """
        symbol, *attributes = row
        for i, attr in enumerate(attributes):
            var = self.get_variable_name(symbol, date, i)
            val = self.clean_value(attr)
            if val:
                yield (var, val)


class StockDataset(FileDataset, StockBase):
    def get_tuples(self, fileobj):
        for row in self.get_tsv_reader(fileobj):
            date, source, *rest = row
            for var, val in self.get_var_vals(rest, date):
                yield (source, var, val)


class SupervisedStockData(FileSupervisedData, StockBase):
    def get_pairs(self, fileobj):
        for row in self.get_tsv_reader(fileobj):
            date, *rest = row
            yield from self.get_var_vals(rest, date)


def usage(stream=sys.stdout):
    print("usage: {} DATA_TSV TRUTH_TSV".format(sys.argv[0]), file=stream)


def main():
    # Show usage
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        usage()
        sys.exit(0)

    try:
        data_path, truth_path = sys.argv[1:]
    except ValueError:
        usage(sys.stderr)
        sys.exit(1)

    print("loading data...")
    start = time.time()
    dataset = StockDataset(data_path)
    end = time.time()
    print("  loaded in {:.3f} seconds".format(end - start))
    print("dataset has {} sources, {} claims, {} variables".format(
        dataset.num_sources, dataset.num_claims, dataset.num_variables
    ))

    print("loading true values...")
    start = time.time()
    sup = SupervisedStockData(dataset, truth_path)
    end = time.time()
    print("  loaded in {:.3f} seconds".format(end - start))
    print("")

    algorithms = [
        MajorityVoting(), Sums(), AverageLog(), Investment(),
        PooledInvestment(), TruthFinder()
    ]

    for alg in algorithms:
        print("running {}...".format(alg.__class__.__name__))
        res = alg.run(sup.data)
        acc = sup.get_accuracy(res)
        print("  {:.3f} seconds, {:.3f} accuracy".format(res.time_taken, acc))


if __name__ == "__main__":
    main()
