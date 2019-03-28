"""
Script to generate graphs included in the project report.
"""
import inspect
import os
import sys

from truthdiscovery import (
    ConvergenceIterator,
    Dataset,
    DistanceMeasures,
    GraphRenderer,
    PlainColourScheme,
    Sums
)


class ReportRenderer(GraphRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colours = PlainColourScheme()

    def get_var_label(self, _var_id):
        return ""

    def get_claim_label(self, _var_id, val_hash):
        return self.dataset.val_hashes.inverse[val_hash]


def example(func):
    """
    Decorator to mark a method as being a graph generation method
    """
    func.example_method = True
    return func


class ExampleFigureCreator:
    def write_all(self, outdir):
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if not hasattr(method, "example_method"):
                continue

            path = os.path.join(outdir, "{}.png".format(name))
            print("writing to {}".format(path))
            with open(path, "wb") as outfile:
                method(outfile)

    @example
    def sums_not_all_equal_trust(self, outfile):
        dataset = Dataset((
            ("A", "obj1", "D"),
            ("A", "obj2", "E"),
            ("B", "obj1", "D"),
            ("C", "obj2", "E")
        ))
        renderer = ReportRenderer(node_size=0.5, font_size=30)
        renderer.draw(dataset, outfile)

    @example
    def sums_non_independence(self, outfile):
        dataset = Dataset((
            ("A", "obj1", "D"),
            ("A", "obj2", "E"),
            ("B", "obj1", "D"),
            ("C", "obj2", "E"),

            ("S", "obj3", "V"),
            ("S", "obj4", "W"),
            ("S", "obj5", "X"),

            ("T", "obj3", "V"),
            ("T", "obj4", "W"),
            ("T", "obj5", "X"),

            ("U", "obj3", "V"),
            ("U", "obj4", "W"),
            ("U", "obj5", "X"),
        ))
        renderer = ReportRenderer(node_size=0.8, font_size=30)
        renderer.draw(dataset, outfile)


if __name__ == "__main__":
    try:
        outdir = sys.argv[1]
    except IndexError:
        print("usage: {} OUTPUT_DIR".format(sys.argv[0]), file=sys.stderr)
        print("create example images and save in OUTPUT_DIR", file=sys.stderr)
        sys.exit(1)

    creator = ExampleFigureCreator()
    creator.write_all(outdir)
