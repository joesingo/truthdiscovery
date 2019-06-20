"""
Script to load a real-world dataset of stock market data, and perform
truth discovery.
"""
import csv
import sys
import time
import pickle

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
    print("       {} PICKLE_FILE".format(sys.argv[0]), file=stream)


def main():
    # Show usage
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        usage()
        return

    dataset = None
    sup = None

    # Unpickle dataset from a file if only one argument given
    if len(sys.argv) == 2:
        print("unpickling data...")
        start = time.time()
        with open(sys.argv[1], "rb") as pickle_file:
            sup = pickle.load(pickle_file)
        end = time.time()
        print("  unpickled in {:.3f} seconds".format(end - start))
        dataset = sup.data

    elif len(sys.argv) == 3:
        data_path, truth_path = sys.argv[1:]
        print("loading data...")
        start = time.time()
        dataset = StockDataset(data_path)
        end = time.time()
        print("  loaded in {:.3f} seconds".format(end - start))

        print("loading true values...")
        start = time.time()
        sup = SupervisedStockData(dataset, truth_path)
        end = time.time()
        print("  loaded in {:.3f} seconds".format(end - start))

        pickle_path = "/tmp/stock_data.pickle"
        with open(pickle_path, "wb") as pickle_file:
            pickle.dump(sup, pickle_file)
        print("pickled to {}".format(pickle_path))

    else:
        usage(sys.stderr)
        sys.exit(1)

    print("")
    print("dataset has {} sources, {} claims, {} variables".format(
        dataset.num_sources, dataset.num_claims, dataset.num_variables
    ))

    start = time.time()
    print("calculating connected components...")
    components = dataset.num_connected_components()
    end = time.time()
    print("  calculated in {:.3f} seconds: {} components".format(
        end - start, components
    ))

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
