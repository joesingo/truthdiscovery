"""
Script to generate graphs included in the project report.
"""
import inspect
from io import BytesIO
import os
import sys

import cairo

from truthdiscovery import (
    Dataset,
    GraphRenderer,
    PlainColourScheme,
    Result,
    ResultsGradientColourScheme
)


class ReportRenderer(GraphRenderer):
    def __init__(self, *args, var_labels=False, **kwargs):
        # Set defaults: these may get overridden in super constructor from
        # kwargs
        kwargs.setdefault("colours", PlainColourScheme())
        kwargs.setdefault("font_size", 30)
        super().__init__(*args, **kwargs)
        self.var_labels = var_labels

    def get_var_label(self, var_id):
        if self.var_labels:
            return super().get_var_label(var_id)
        return ""

    def get_claim_label(self, _var_id, val_hash):
        return self.dataset.val_hashes.inverse[val_hash]


class ColouredNodesColourScheme(PlainColourScheme):
    """
    Colour scheme that allows choosing the colours of specific nodes
    """
    def __init__(self, colour_mapping):
        """
        :param colour_mapping: a dict mapping source name/variable name/claim
                               value to RGB tuple for nodes that should have
                               specific colours
        """
        self.colour_mapping = colour_mapping

    def get_node_colour(self, node_type, hints):
        if isinstance(hints, tuple):
            _, name = hints
        else:
            name = hints

        defaults = super().get_node_colour(node_type, hints)
        if name not in self.colour_mapping:
            return defaults

        node, label, _ = defaults
        return node, label, self.colour_mapping[name]


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
        renderer = ReportRenderer(node_size=0.5)
        renderer.render(dataset, outfile)

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
        renderer = ReportRenderer(node_size=0.8)
        renderer.render(dataset, outfile)

    @example
    def independence_illustration_1(self, outfile):
        dataset = Dataset((
            ("S", "O", "A"),
            ("T", "O", "B"),
            ("T", "P", "C"),
            ("T", "Q", "D"),

            ("U", "P", "C"),
            ("U", "Q", "D"),

            ("V", "P", "C"),
            ("V", "Q", "D")
        ))
        renderer = ReportRenderer(var_labels=True)
        renderer.render(dataset, outfile)

    @example
    def visualisation_example(self, outfile):
        dataset = Dataset((
            ("source 1", "var 1", "7"),
            ("source 2", "var 1", "7"),
            ("source 3", "var 1", "8"),
            ("source 4", "var 1", "7"),
            ("source 5", "var 1", "43"),

            ("source 1", "var 2", "dark red"),
            ("source 2", "var 2", "green"),
            ("source 3", "var 2", "red"),
            ("source 4", "var 2", "dark red"),
            ("source 5", "var 2", "green")
        ))
        results = Result(
            trust={
                "source 1": 1.0,
                "source 2": 0.5,
                "source 3": 0.5,
                "source 4": 0.75,
                "source 5": 0.1
            },
            belief={
                "var 1": {
                    "7": 0.9, "8": 0.3, "43": 0.01
                },
                "var 2": {
                    "green": 0.7, "red": 0.9, "dark red": 0.93
                }
            },
            time_taken=None
        )
        colours = ResultsGradientColourScheme(results)
        renderer = ReportRenderer(
            var_labels=True, colours=colours, font_size=18
        )
        renderer.render(dataset, outfile)

    @example
    def independence_illustration_2(self, outfile):
        dataset = Dataset((
            ("S", "O", "A"),
            ("T", "O", "B"),

            ("U", "P", "C"),
            ("U", "Q", "D"),

            ("V", "P", "C"),
            ("V", "Q", "D")
        ))
        renderer = ReportRenderer(var_labels=True)
        renderer.render(dataset, outfile)

    @example
    def symmetry_example(self, outfile):
        dataset1 = Dataset((
            ("S", "O", "A"),
            ("S", "P", "C"),
            ("T", "O", "A"),
            ("U", "O", "B")
        ))
        dataset2 = Dataset((
            ("S", "O", "A"),
            ("T", "O", "B"),
            ("T", "P", "C"),
            ("U", "O", "B")
        ))
        # Colours for nodes
        red = (0.8235294117647058, 0.0, 0.12941176470588237)
        green = (0.0, 0.5647058823529412, 0.4235294117647059)
        blue = (0.043137254901960784, 0.27450980392156865, 0.5725490196078431)
        yellow = (0.8705882352941177, 0.5372549019607843, 0.0)
        purple = (0.5647058823529412, 0, 0.5647058823529412)
        colours1 = {
            "S": blue,
            "T": green,
            "U": red,
            "A": yellow,
            "B": purple
        }
        colours2 = {
            "S": red,
            "T": blue,
            "U": green,
            "A": purple,
            "B": yellow
        }

        # Draw networks to in-memory buffers
        buf1 = BytesIO()
        buf2 = BytesIO()
        renderer = ReportRenderer(
            var_labels=True, node_size=0.6, node_border_width=6
        )
        renderer.colours = ColouredNodesColourScheme(colours1)
        renderer.render(dataset1, buf1)
        renderer.colours = ColouredNodesColourScheme(colours2)
        renderer.render(dataset2, buf2)
        buf1.seek(0)
        buf2.seek(0)

        # Create image of both networks side-by-side
        margin = 100
        w = margin + 2 * renderer.width
        h = renderer.height
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)
        # Fill surface with background colour
        ctx.set_source_rgba(*renderer.colours.get_background_colour())
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Draw vertical line separating the networks
        ctx.set_source_rgba(0.5, 0.5, 0.5)
        ctx.set_line_width(3)
        ctx.move_to(w / 2, 0)
        ctx.line_to(w / 2, h)
        ctx.stroke()

        img1 = cairo.ImageSurface.create_from_png(buf1)
        img2 = cairo.ImageSurface.create_from_png(buf2)
        ctx.set_source_surface(img1, 0, 0)
        ctx.paint()
        ctx.set_source_surface(img2, w - renderer.width, 0)
        ctx.paint()
        surface.write_to_png(outfile)


if __name__ == "__main__":
    outdir = None
    try:
        outdir = sys.argv[1]
    except IndexError:
        print("usage: {} OUTPUT_DIR".format(sys.argv[0]), file=sys.stderr)
        print("create example images and save in OUTPUT_DIR", file=sys.stderr)
        sys.exit(1)

    creator = ExampleFigureCreator()
    creator.write_all(outdir)
