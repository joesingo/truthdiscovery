import sys
from csv import DictReader
from os import path

import numpy.ma as ma

from truthdiscovery.input import Dataset


CSV_FILE = path.join(path.dirname(__file__), "data.csv")


def main():
    var_num_mapping = {}
    source_num_mapping = {}
    val_mapping = {}
    sv_entries = []

    with open(CSV_FILE) as f:
        reader = DictReader(f, skipinitialspace=True)
        for row in reader:
            var_id = row["ObjectID"]
            source_id = row["SourceID"]
            val = row["PropertyValue"]

            if var_id not in var_num_mapping:
                var_num_mapping[var_id] = len(var_num_mapping)
            if source_id not in source_num_mapping:
                source_num_mapping[source_id] = len(source_num_mapping)
            if val not in val_mapping:
                val_mapping[val] = len(val_mapping)

            sv_entries.append(
                (source_num_mapping[source_id], var_num_mapping[var_id],
                 val_mapping[val])
            )

    sv_mat = ma.masked_all((len(source_num_mapping), len(var_num_mapping)))
    for source, var, val in sv_entries:
        sv_mat[source, var] = val

    print(Dataset(sv_mat).to_csv())


if __name__ == "__main__":
    main()
