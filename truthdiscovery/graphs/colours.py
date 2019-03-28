from enum import Enum


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
        """
        Return background colour for the graph
        """
        return (1, 1, 1)  # white

    def get_edge_colour(self):
        """
        Return colour for the edges between nodes
        """
        return (0.5, 0.5, 0.5)  # grey

    def get_animation_progress_colour(self):
        """
        Return colour for the bar displaying animation progress
        """
        return (0, 0, 0)  # black


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


class PlainColourScheme(GraphColourScheme):
    """
    Plain black and white colour scheme
    """
    def get_node_colour(self, *args):
        return (1, 1, 1), (0, 0, 0), (0, 0, 0)

    def get_edge_colour(self):
        return (0, 0, 0)
