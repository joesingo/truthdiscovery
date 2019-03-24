from enum import Enum
import math

import cairo
import numpy as np


class NodeType(Enum):
    SOURCE = "source"
    CLAIM = "claim"
    VARIABLE = "variable"


class GraphColourScheme:
    """
    Default colour scheme for graphs
    """
    def get_node_colour(self, node_type, hints):
        """
        :param node_type: value from :any:`NodeType` enumeration
        :param hints:     for variables and sources: var/source ID. For claims,
                          a tuple (var, val)
        :return: `(node_colour, label_colour, border_colour)`
        """
        node_colour = None
        if node_type == NodeType.SOURCE:
            node_colour = (0.133, 0.40, 0.40)  # turquoise
        elif node_type == NodeType.CLAIM:
            node_colour = (0.478, 0.624, 0.208)  # green
        else:
            node_colour = (0.667, 0.224, 0.224)  # red

        label_colour = (1, 1, 1)            # white labels
        border_colour = (0.15, 0.15, 0.15)  # dark grey border

        return node_colour, label_colour, border_colour

    def get_background_colour(self):
        return (1, 1, 1)  # white

    def get_edge_colour(self):
        return (0.5, 0.5, 0.5)  # grey


class ResultsGradientColourScheme(GraphColourScheme):
    """
    Colour scheme where the colour for a source/claim depends on its
    trust/belief score in a given set of results
    """
    # Colours obtained from here:
    # http://colorbrewer2.org/?type=sequential&scheme=Greens&n=9
    COLOURS = [
        # Lowest value (pale colour)
        (0.9686274509803922, 0.9882352941176471, 0.9607843137254902),
        (0.8980392156862745, 0.9607843137254902, 0.8784313725490196),
        (0.7803921568627451, 0.9137254901960784, 0.7529411764705882),
        (0.6313725490196078, 0.8509803921568627, 0.6078431372549019),
        (0.4549019607843137, 0.7686274509803922, 0.4627450980392157),
        (0.2549019607843137, 0.6705882352941176, 0.36470588235294116),
        (0.13725490196078433, 0.5450980392156862, 0.27058823529411763),
        (0.0, 0.42745098039215684, 0.17254901960784313),
        # Highest value (dark green)
        (0.0, 0.26666666666666666, 0.10588235294117647)
    ]
    LIGHT_LABEL = (1, 1, 1)  # white
    DARK_LABEL = (0, 0, 0)   # black

    def __init__(self, results):
        self.results = results

    def get_graded_colours(self, level):
        """
        :param level: a float in [0, 1]
        :return: (interior, label) RGB triples for the colours corresponding to
                 the given level
        """
        # Quantise level to an integer in [0, num_colours)
        index = min(int(level * len(self.COLOURS)), len(self.COLOURS) - 1)
        label_colour = self.DARK_LABEL if level < 0.5 else self.LIGHT_LABEL
        return self.COLOURS[index], label_colour

    def get_node_colour(self, node_type, hints):
        defaults = super().get_node_colour(node_type, hints)
        default_node, default_label, default_border = defaults

        # We can only use graded colours for sources and claims, so stick to
        # defaults in parent class for variables
        if node_type == NodeType.VARIABLE:
            return defaults

        # Get level from hint
        if isinstance(hints, tuple):
            var, val = hints
            level = self.results.belief[var][val]
        else:
            source = hints
            level = self.results.trust[source]

        node_colour, label_colour = self.get_graded_colours(level)
        return node_colour, label_colour, default_border


class GraphRenderer:
    """
    Create an image that shows a graph representation of a truth-discovery
    dataset
    """
    def __init__(self, dataset, width=800, height=600, node_size=0.8,
                 line_width=3, node_border_width=3, font_size=15,
                 colours=None):
        """
        :param dataset:           :any:`Dataset` object
        :param width:             width of image in pixels
        :param height:            height of image in pixels
        :param node_size:         number in [0, 1] to control node size. 1 is
                                  maximum size -- nodes will be touching in
                                  this case
        :param node_border_width: width in pixels of node border (use None or 0
                                  for no border)
        :param line_width:        with in pixels for edges between nodes
        :param font_size:         font size for node labels
        :param colours:           :any:`GraphColourScheme` (or sub-class)
                                  instance
        """
        self.dataset = dataset
        self.width = width
        self.height = height
        self.node_size = node_size
        self.node_border_width = node_border_width or 0
        self.colours = colours or GraphColourScheme()

        # Work out maximum pixels that can be allocated to each node without
        # vertical overlapping
        max_vertical_nodes = max(
            self.dataset.num_sources,
            self.dataset.num_claims,
            self.dataset.num_variables
        )
        max_px_per_node = self.height / max_vertical_nodes

        # Radius is a proportion of this maximum size
        self.node_radius = max_px_per_node * self.node_size / 2

        # Distance between image corners and centres of corner nodes. It is
        # calculated such that nodes will meet the corners exactly when
        # node_size is 1
        self.offset = max_px_per_node / 2

        # Initialise Cairo and draw background
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, self.width, self.height
        )
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_line_width(line_width)
        self.ctx.set_font_size(font_size)
        self.ctx.set_source_rgb(*self.colours.get_background_colour())
        self.ctx.rectangle(0, 0, self.width, self.height)
        self.ctx.fill()

    def _get_y_coord(self, index, num_nodes):
        available_height = self.height - 2 * self.offset
        return self.offset + available_height * index / (num_nodes - 1)

    def get_source_coords(self, source_id):
        y = self._get_y_coord(source_id, self.dataset.num_sources)
        return (self.offset, y)

    def get_var_coords(self, var_id):
        y = self._get_y_coord(var_id, self.dataset.num_variables)
        return (self.width - self.offset, y)

    def get_claim_coords(self, index):
        y = self._get_y_coord(index, self.dataset.num_claims)
        return (self.width / 2, y)

    def get_source_label(self, source_id):
        return self.dataset.source_ids.inverse[source_id]

    def get_var_label(self, var_id):
        return self.dataset.var_ids.inverse[var_id]

    def get_claim_label(self, var_id, val_hash):
        return "{var} = {val}".format(
            var=self.dataset.var_ids.inverse[var_id],
            val=self.dataset.val_hashes.inverse[val_hash]
        )

    def draw(self, outfile):
        """
        Draw the dataset as a graph and save as a PNG

        :param outfile: file object to write to
        """
        # We want to position claims so that claims for the same variable are
        # next to each other: sort claims by their variable ID and construct a
        # map claim ID -> index to do this
        claim_indexes = {}
        var_claim_pairs = (
            (var_id, claim_id)
            for (var_id, _), claim_id in self.dataset.claim_ids.items()
        )
        for i, (_, claim_id) in enumerate(sorted(var_claim_pairs)):
            claim_indexes[claim_id] = i

        # Draw edges between sources and claims
        for s_id, claim_id in np.transpose(np.nonzero(self.dataset.sc)):
            start = self.get_source_coords(s_id)
            end = self.get_claim_coords(claim_indexes[claim_id])
            self.draw_edge(start, end)

        # Draw claims, variables and sources
        for (var_id, val_hash), claim_id in self.dataset.claim_ids.items():
            # Draw edge from claim to variable
            claim_coords = self.get_claim_coords(claim_indexes[claim_id])
            var_coords = self.get_var_coords(var_id)
            self.draw_edge(claim_coords, var_coords)

            label = self.get_claim_label(var_id, val_hash)
            hint = (
                self.dataset.var_ids.inverse[var_id],      # variable name
                self.dataset.val_hashes.inverse[val_hash]  # value
            )
            self.draw_node(NodeType.CLAIM, label, claim_coords, hint)

        for var, var_id in self.dataset.var_ids.items():
            label = self.get_var_label(var_id)
            coords = self.get_var_coords(var_id)
            self.draw_node(NodeType.VARIABLE, label, coords, var)

        for source, s_id in self.dataset.source_ids.items():
            label = self.get_source_label(s_id)
            coords = self.get_source_coords(s_id)
            self.draw_node(NodeType.SOURCE, label, coords, source)

        self.write_to_file(outfile)

    def write_to_file(self, outfile):
        """
        Save the current Cairo surface to the given file
        """
        self.surface.write_to_png(outfile)

    def draw_node(self, node_type, label, coords, node_hints):
        """
        :param node_type:  value from :any:`NodeType` enumeration
        :param label:      text to draw for this node
        :param coords:     a tuple (x, y)
        :param node_hints: data that identifies the node, which is forwarded to
                           colour scheme to get node colour
        """
        node_c, label_c, border_c = self.colours.get_node_colour(
            node_type, node_hints
        )

        # Draw circle for the node
        x, y = coords
        # first draw solid border colour...
        if self.node_border_width > 0:
            self.ctx.set_source_rgb(*border_c)
            self.ctx.arc(x, y, self.node_radius, 0, 2 * math.pi)
            self.ctx.fill()
        # then interior
        self.ctx.set_source_rgb(*node_c)
        self.ctx.arc(
            x, y, self.node_radius - self.node_border_width, 0, 2 * math.pi
        )
        self.ctx.fill()

        # Label
        ext = self.ctx.text_extents(label)
        # Make sure long source or var names do not run off the screen
        label_lhs = max(0, min(self.width - ext.width, x - ext.width / 2))

        # If label exceeds the node, draw a background-coloured box where text
        # will go, so that the label does not clash with background/node border
        if ext.width > 2 * self.node_radius:
            background = self.colours.get_background_colour()
            r, g, b = background
            self.ctx.set_source_rgb(*background)
            # Try and have label an 'opposite' colour for label to avoid
            # clashing
            label_c = (1 - r, 1 - g, 1 - b)

            padding = 5  # allow some space between box border and text
            self.ctx.rectangle(
                label_lhs - padding,
                y - ext.height / 2 - padding,
                ext.width + 2 * padding,
                ext.height + 2 * padding
            )
            self.ctx.fill()

        self.ctx.set_source_rgb(*label_c)
        self.ctx.move_to(label_lhs, y - ext.y_bearing / 2)
        self.ctx.show_text(label)

    def draw_edge(self, start, end):
        self.ctx.set_source_rgb(*self.colours.get_edge_colour())
        self.ctx.move_to(*start)
        self.ctx.line_to(*end)
        self.ctx.stroke()


class MatrixDatasetGraphRenderer(GraphRenderer):
    """
    Modify node labels for matrix datasets, where source/var labels are just
    ints
    """
    def __init__(self, *args, zero_indexed=True, **kwargs):
        self.zero_indexed = zero_indexed
        super().__init__(*args, **kwargs)

    def format_id(self, int_id):
        if not self.zero_indexed:
            int_id += 1
        return str(int_id)

    def get_source_label(self, source_id):
        return "s{}".format(self.format_id(source_id))

    def get_var_label(self, var_id):
        return "v{}".format(self.format_id(var_id))

    def get_claim_label(self, var_id, val_hash):
        val = str(self.dataset.val_hashes.inverse[val_hash])
        if val.endswith(".0"):
            val = val[:-2]
        return "{}={}".format(self.get_var_label(var_id), val)
