import csv
import random
from os import path
from collections import namedtuple

import numpy as np
import numpy.ma as ma

from truthdiscovery.algorithm import (
    AverageLog,
    Investment,
    MajorityVoting,
    PooledInvestment,
    Sums,
    TruthFinder
)
from truthdiscovery.input.text_dataset import TextDataset
from truthdiscovery.input.supervised_data import SupervisedData


Name = namedtuple("Name", ["first", "last", "middle"])


class BookBase:
    @classmethod
    def get_author_list(self, authors_string):
        def inner():
            for name in authors_string.lower().split(";"):
                name = name.strip()
                if not name:
                    continue

                firsts = []
                lasts = []
                middles = []

                if "," in name:
                    last, other = name.split(",", maxsplit=1)
                    last = last.strip()
                    lasts.append(last)
                    other = other.strip()
                    if " " in other:
                        first, middle = other.split(maxsplit=1)
                        firsts.append(first)
                        middles.append(middle)
                    else:
                        firsts.append(other)

                elif " " in name:
                    first, other = name.split(maxsplit=1)
                    firsts.append(first)
                    if " " in other:
                        rev_last, rev_middle = other[::-1].split(maxsplit=1)
                        lasts.append(rev_last[::-1])
                        middles.append(rev_middle[::-1])
                    else:
                        lasts.append(other)
                else:
                    lasts.append(name)
                name_tuple = Name(tuple(firsts), tuple(lasts), tuple(middles))
                yield name_tuple
        return tuple(inner())


class BookDataset(TextDataset, BookBase):
    def get_tuples(self, fileobj):
        reader = csv.reader(fileobj, delimiter="\t")
        for row in reader:
            source, isbn, _title, authors = row
            yield (source, isbn, self.get_author_list(authors))


class BookSupervisedData(SupervisedData, BookBase):
    def __init__(self, claims_filename, true_values_filename):
        print("Loading data...")
        with open(claims_filename) as claims_file:
            data = BookDataset(claims_file)

        print("Loading true values...")
        values = ma.masked_all((data.num_variables,))
        with open(true_values_filename) as values_file:
            reader = csv.reader(values_file, delimiter="\t")
            for row in reader:
                if not row:
                    continue
                isbn, authors = row
                var_id = data.var_ids[isbn]
                key = (isbn, self.get_author_list(authors))
                try:
                    val = data.val_hashes[key]
                except KeyError:
                    # No source made the correct claim
                    continue
                values[var_id] = val
        if np.all(values.mask == True):
            raise ValueError(
                "Did not parse any true values from '{}'"
                .format(true_values_filename)
            )
        super().__init__(data, values)

    def get_accuracy(self, results):
        summed_acc = 0
        count = 0
        for var, true_value in enumerate(self.values):
            if ma.is_masked(true_value):
                continue
            most_believed = random.choice(
                list(results.get_most_believed_values(var))
            )
            _, claimed_tuple = self.data.val_hashes.inverse[most_believed]
            _, real_tuple = self.data.val_hashes.inverse[true_value]
            claimed = set(claimed_tuple)
            real = set(real_tuple)
            x = len(real)
            y = len(claimed)
            z = 0
            for first, last, middle in claimed:
                scores = []
                for r_first, r_last, r_middle in real:
                    score = 0
                    if r_middle:
                        denom = 6
                        if middle == r_middle:
                            score += 1 / 6
                        elif middle and middle[0] == r_middle[0]:
                            score += 1 / 12
                    else:
                        denom = 5
                    if last == r_last:
                        score += 3 / denom
                    if first == r_first:
                        score += 2 / denom
                    elif first and first[0] == r_first[0]:
                        score += 1 / denom
                    scores.append(score)
                z += max(scores)

            acc = z / max(y, x)
            summed_acc += acc
            count += 1
        return summed_acc / count

if __name__ == "__main__":
    here = path.dirname(__file__)
    claims_filename = path.join(here, "book.txt")
    true_values_filename = path.join(here, "book_golden.txt")
    sup = BookSupervisedData(claims_filename, true_values_filename)

    algs = [
        AverageLog,
        Investment,
        MajorityVoting,
        PooledInvestment,
        Sums,
        TruthFinder
    ]
    for alg_cls in algs:
        alg = alg_cls()
        res = alg.run(sup.data)
        accuracy = sup.get_accuracy(res)
        try:
            iterations = alg.iterator.it_count
        except AttributeError:
            iterations = "n/a"
        print(
            "{}: {:.3f} ({} iterations)"
            .format(alg.__class__.__name__, accuracy, iterations)
        )
