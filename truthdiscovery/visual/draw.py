import math

import cairo
import numpy as np


class GraphRenderer:
    """
    Create an image that shows a graph representation of a truth-discovery
    dataset
    """
    COLOURS = {
        "source": (0.133, 0.40, 0.40),   # turquoise
        "claim": (0.667, 0.224, 0.224),  # red
        "var": (0.478, 0.624, 0.208),    # green
        "label": (1, 1, 1),              # white
        "edge": (0.5, 0.5, 0.5),         # grey
        "background": (1, 1, 1)          # white
    }

    def __init__(self, dataset, width=800, height=600, node_size=0.75,
                 line_width=3, font_size=15):
        """
        :param dataset:    :any:`Dataset` object
        :param width:      width of image in pixels
        :param height:     height of image in pixels
        :param node_size:  number in [0, 1] to control node size. 1 is maximum
                           size -- nodes will be touching in this case
        :param line_width: with in pixels for edges between nodes
        :param font_size:  font size for node labels
        """
        self.dataset = dataset
        self.width = width
        self.height = height
        self.node_size = node_size

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
        self.ctx.set_source_rgb(*self.COLOURS["background"])
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
            self.draw_node("claim", label, claim_coords)

        for var_id in self.dataset.var_ids.values():
            label = self.get_var_label(var_id)
            coords = self.get_var_coords(var_id)
            self.draw_node("var", label, coords)

        for s_id in self.dataset.source_ids.values():
            label = self.get_source_label(s_id)
            coords = self.get_source_coords(s_id)
            self.draw_node("source", label, coords)

        self.write_to_file(outfile)

    def write_to_file(self, outfile):
        """
        Save the current Cairo surface to the given file
        """
        self.surface.write_to_png(outfile)

    def draw_node(self, kind, label, coords):
        """
        :param kind: one of 'source', 'claim' or 'var'
        :param label: text to draw for this node
        :param coords: a tuple (x, y)
        """
        # Draw circle for the node
        x, y = coords
        self.ctx.set_source_rgb(*self.COLOURS[kind])
        self.ctx.arc(x, y, self.node_radius, 0, 2 * math.pi)
        self.ctx.fill()

        # Draw the label
        self.ctx.set_source_rgb(*self.COLOURS["label"])
        ext = self.ctx.text_extents(label)
        self.ctx.move_to(x - ext.width / 2, y - ext.y_bearing / 2)
        self.ctx.show_text(label)

    def draw_edge(self, start, end):
        self.ctx.set_source_rgb(*self.COLOURS["edge"])
        self.ctx.move_to(*start)
        self.ctx.line_to(*end)
        self.ctx.stroke()
