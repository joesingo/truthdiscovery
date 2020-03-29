import math

import numpy as np

from truthdiscovery.graphs.backends import PngBackend
from truthdiscovery.graphs.colours import NodeType, GraphColourScheme
from truthdiscovery.graphs.entities import Rectangle, Circle, Line, Label


def _sort_keys_by_value(dct):
    """
    :param dct: a dictionary
    :return: a list of the keys in ``dict`` sorted by their corresponding value
    """
    return sorted(dct, key=lambda key: dct[key])


class GraphRenderer:
    """
    Create an image that shows a graph representation of a truth discovery
    dataset
    """
    def __init__(self, width=800, node_radius=50, spacing=20, line_width=3,
                 node_border_width=3, font_size=15, colours=None,
                 backend=None):
        """
        :param width:             width of the image in pixels
        :param node_radius:       node radius in pixels
        :param spacing:           minimum vertical spacing between nodes in
                                  pixels
        :param node_border_width: width in pixels of node border (use None or 0
                                  for no border)
        :param line_width:        with in pixels for edges between nodes
        :param font_size:         font size for node labels
        :param colours:           :any:`GraphColourScheme` (or sub-class)
                                  instance
        :param backend:           a :any:`BaseBackend` object (default is PNG)
        """
        self.width = width
        # Height is calculated based on the number of nodes, so is set later
        self.height = None

        self.node_radius = node_radius
        self.spacing = spacing
        self.node_border_width = node_border_width or 0
        self.line_width = line_width
        self.font_size = font_size
        self.colours = colours or GraphColourScheme()
        self.backend = backend or PngBackend()

        self.dataset = None

    def _get_y_coord(self, index, num_nodes):
        if num_nodes > 1:
            available_height = self.height - 2 * self.node_radius
            return (self.node_radius
                    + available_height * index / (num_nodes - 1))
        return self.height / 2

    def get_source_coords(self, index):
        y = self._get_y_coord(index, self.dataset.num_sources)
        return (self.node_radius, y)

    def get_var_coords(self, index, claim_y_coords):
        y = np.mean(claim_y_coords)
        return (self.width - self.node_radius, y)

    def get_claim_coords(self, index):
        y = self._get_y_coord(index, self.dataset.num_claims)
        return (self.width - self.node_radius, y)

    def get_source_label(self, source_id):
        return self.dataset.source_ids.inverse[source_id]

    def get_var_label(self, var_id):
        return self.dataset.var_ids.inverse[var_id]

    def get_claim_label(self, var_id, val_hash):
        return "{var} = {val}".format(
            var=self.dataset.var_ids.inverse[var_id],
            val=self.dataset.val_hashes.inverse[val_hash]
        )

    def get_height(self, dataset):
        max_vertical_nodes = max(
            dataset.num_sources,
            dataset.num_claims,
            dataset.num_variables
        )
        nodes_px = max_vertical_nodes * 2 * self.node_radius
        spacing_px = (max_vertical_nodes - 1) * self.spacing
        return int(nodes_px + spacing_px)

    def render(self, dataset, outfile, animation_progress=None):
        """
        :param dataset:            a :any:`Dataset` object
        :param outfile:            file object to write to
        :param animation_progress: percentage animation progress in [0, 1] to
                                   display how far through an animation we are
                                   (None if not animating)
        """
        self.height = self.get_height(dataset)
        entities = self.compile(dataset, animation_progress=animation_progress)
        self.backend.draw_entities(entities, outfile, self.width, self.height)

    def compile(self, dataset, animation_progress=None):
        """
        A generator of :any:`Entity` objects describing what to draw and in
        which order
        """
        if not self.height:
            # This allows `compile` to be called directly in tests...
            self.height = self.get_height(dataset)

        yield from self.compile_background()
        self.dataset = dataset

        # Get labels for nodes
        source_labels = {}
        var_labels = {}
        claim_labels = {}

        for s_id in self.dataset.source_ids.values():
            source_labels[s_id] = self.get_source_label(s_id)
        for var_id in self.dataset.var_ids.values():
            var_labels[var_id] = self.get_var_label(var_id)
        for ((var_id, val_hash), claim_id) in self.dataset.claim_ids.items():
            claim_labels[claim_id] = self.get_claim_label(var_id, val_hash)

        # Get y-coordinates for all nodes. We sort nodes of each type by their
        # label to determine the ordering
        source_coords = {}
        var_coords = {}
        claim_coords = {}
        for i, s_id in enumerate(_sort_keys_by_value(source_labels)):
            source_coords[s_id] = self.get_source_coords(i)
        # For claims, we sort first by variable label and then by claim label:
        # this ensures that claims for the same variable are all next to each
        # other
        claim_sort_keys = {}
        for ((var_id, _), claim_id) in self.dataset.claim_ids.items():
            sort_key = (var_labels[var_id], claim_labels[claim_id])
            claim_sort_keys[claim_id] = sort_key
        for i, claim_id in enumerate(_sort_keys_by_value(claim_sort_keys)):
            claim_coords[claim_id] = self.get_claim_coords(i)
        # For variables, average use y-coords of the associated claims
        for i, var_id in enumerate(_sort_keys_by_value(var_labels)):
            claim_ys = [
                claim_coords[c_id][1]
                for (v_id, _), c_id in self.dataset.claim_ids.items()
                if v_id == var_id
            ]
            var_coords[var_id] = self.get_var_coords(i, claim_ys)

        # Draw edges between sources and claims
        for s_id, claim_id in np.transpose(np.nonzero(self.dataset.sc)):
            _, val_hash = self.dataset.claim_ids.inverse[claim_id]
            hint = (
                self.dataset.source_ids.inverse[s_id],     # source label
                self.dataset.val_hashes.inverse[val_hash]  # value
            )
            yield from self.compile_edge(
                source_coords[s_id], claim_coords[claim_id], hint
            )
            yield from self.compile_edge(
                claim_coords[claim_id], source_coords[s_id], hint
            )

        # Amsterdam slides hack: draw edges between claims for the same object
        for (var1, _), cid1 in self.dataset.claim_ids.items():
            for (var2, _), cid2 in self.dataset.claim_ids.items():
                if cid1 == cid2 or var1 != var2:
                    continue
                yield from self.compile_edge(
                    claim_coords[cid1], claim_coords[cid2], ("", "")
                )
                yield from self.compile_edge(
                    claim_coords[cid2], claim_coords[cid1], ("", "")
                )

        # Draw claims, variables and sources
        for (var_id, val_hash), claim_id in self.dataset.claim_ids.items():
            # # Draw edge from claim to variable
            # hint = (
            #     self.dataset.val_hashes.inverse[val_hash],  # value
            #     self.dataset.var_ids.inverse[var_id]        # variable name
            # )
            # yield from self.compile_edge(
            #     claim_coords[claim_id], var_coords[var_id], hint
            # )

            # Draw claim
            hint = (
                self.dataset.var_ids.inverse[var_id],      # variable name
                self.dataset.val_hashes.inverse[val_hash]  # value
            )
            yield from self.compile_node(
                NodeType.CLAIM, claim_labels[claim_id], claim_coords[claim_id],
                hint
            )

        # # Variables
        # for var, var_id in self.dataset.var_ids.items():
        #     coords = var_coords[var_id]
        #     label = var_labels[var_id]
        #     yield from self.compile_node(NodeType.VARIABLE, label, coords, var)

        # Sources
        for source, s_id in self.dataset.source_ids.items():
            coords = source_coords[s_id]
            label = source_labels[s_id]
            yield from self.compile_node(
                NodeType.SOURCE, label, coords, source
            )

        # Draw animation progress bar if required
        if animation_progress is not None:
            yield from self.compile_animation_progress_rect(animation_progress)

    def compile_background(self):
        """
        Yield a Rectangle for the background
        """
        yield Rectangle(
            x=0, y=0, width=self.width, height=self.height,
            colour=self.colours.get_background_colour()
        )

    def compile_node(self, node_type, label, coords, node_hints):
        """
        Return a generator of :any:`Entity` objects for drawing a node.

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
        # First solid border colour...
        if self.node_border_width > 0:
            yield Circle(x=x, y=y, colour=border_c, radius=self.node_radius)
        # ...then the interior
        label = Label(
            x=x, y=y, colour=label_c,
            text=str(label),
            size=self.font_size,
            overflow_background=self.colours.get_background_colour()
        )
        yield Circle(
            x=x, y=y, colour=node_c,
            radius=self.node_radius - self.node_border_width,
            label=label
        )

    def compile_edge(self, start, end, edge_hints):
        start_x, start_y = start
        end_x, end_y = end
        colour = self.colours.get_edge_colour()

        src, dest = edge_hints
        if src in ("s", "t", "u", "v"):
            colour = (0.09, 0.64, 0.09)
        else:
            colour = (1, 0.25, 0.25)

        yield Line(
            x=start_x, y=start_y, colour=colour, end_x=end_x, end_y=end_y,
            width=self.line_width, dashed=self.is_dashed(edge_hints)
        )
        # Yield lines for arrow head
        arrow_size = 10
        arrow_angle = math.pi / 7
        edge_inclination = math.atan2(end_y - start_y, end_x - start_x)
        # Calculate the point where edge crosses the node circle
        vec = np.array([-self.node_radius, 0])
        vec = self.rotation_matrix(edge_inclination) @ vec
        node_crossing = np.array(end) + vec

        for s in (-1, 1):
            # Here we consider the vector that starts at `node_crossing` and
            # takes us along the top/bottom arrow head. Start by imagining
            # arrow head is horizontal, then rotate to get the desired angle
            # wrt the edge
            displacement = np.array([-arrow_size, 0])
            angle = s * arrow_angle + edge_inclination
            displacement = self.rotation_matrix(angle) @ displacement
            arrow_end = node_crossing + displacement
            yield Line(
                x=node_crossing[0], y=node_crossing[1], end_x=arrow_end[0],
                end_y=arrow_end[1], width=self.line_width, colour=colour
            )

    def compile_animation_progress_rect(self, progress):
        """
        Return a :any:`Rectangle` for a bar across the bottom of the image to
        indicate progress through an animation

        :param progress: number in [0, 1] indicating width of the bar as a
                         fraction of total image width
        """
        colour = self.colours.get_animation_progress_colour()
        size = 5
        yield Rectangle(
            x=0,
            y=self.height - size,
            colour=colour,
            width=self.width * progress,
            height=size
        )

    def is_dashed(self, edge_hints):
        """
        Return a bool indicating whether a given edge should be dashed

        :param edge_hints: forwarded hints about an edge
        """
        return False

    @classmethod
    def rotation_matrix(cls, angle):
        return np.array([
            [np.cos(angle), -np.sin(angle)],
            [np.sin(angle), np.cos(angle)],
        ])


class MatrixDatasetGraphRenderer(GraphRenderer):
    """
    Modify node labels for matrix datasets, where source/var labels are just
    ints
    """
    def __init__(self, *args, zero_indexed=True, **kwargs):
        self.zero_indexed = zero_indexed
        super().__init__(*args, **kwargs)

    def format_label(self, label):
        if not self.zero_indexed:
            label += 1
        return str(label)

    def get_source_label(self, source_id):
        label = super().get_source_label(source_id)
        return "s{}".format(self.format_label(label))

    def get_var_label(self, var_id):
        label = super().get_var_label(var_id)
        return "v{}".format(self.format_label(label))

    def get_claim_label(self, var_id, val_hash):
        val = str(self.dataset.val_hashes.inverse[val_hash])
        if val.endswith(".0"):
            val = val[:-2]
        return "{}={}".format(self.get_var_label(var_id), val)
