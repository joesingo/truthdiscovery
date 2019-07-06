import sys
import time

from truthdiscovery.input import FileDataset


class TsvDataset(FileDataset):
    """
    Load a dataset from a TSV file, where each line is of the form
        <source> <variable> <value>...
    with each field separated by tabs. Note that there may be several value
    columns
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, allow_multiple=True, **kwargs)

    def get_tuples(self, fileobj):
        for i, line in enumerate(fileobj):
            try:
                source, variable, *val = line.split("\t")
            except ValueError:
                print("malformed input at line {}: ignoring".format(i),
                      file=sys.stderr)
                continue

            yield (source, variable, tuple(val))


def usage(stream=sys.stdout):
    print("usage: {} DATA...".format(sys.argv[0]), file=stream)


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        usage()
        return
    if len(sys.argv) >= 2:
        filepaths = sys.argv[1:]
    else:
        usage(stream=sys.stderr)
        sys.exit(1)

    for filepath in filepaths:
        start = time.time()
        print("loading {}...".format(filepath))
        dataset = TsvDataset(filepath)
        end = time.time()
        print("  loaded in {:.3f} seconds".format(end - start))

        msg = ("dataset has {} sources, {} claims, {} variables, {} connected "
               "components")
        print(msg.format(dataset.num_sources, dataset.num_claims,
                         dataset.num_variables,
                         dataset.num_connected_components()))
        print("")


if __name__ == "__main__":
    main()
