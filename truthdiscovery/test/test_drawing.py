from io import BytesIO
import imageio
import pytest

from truthdiscovery.algorithm import Sums
from truthdiscovery.input import Dataset, MatrixDataset
from truthdiscovery.output import Result
from truthdiscovery.graphs import (
    Animator,
    BaseBackend,
    GraphColourScheme,
    GraphRenderer,
    MatrixDatasetGraphRenderer,
    NodeType,
    PlainColourScheme,
    PngBackend,
    ResultsGradientColourScheme
)
from truthdiscovery.test.utils import is_valid_png, is_valid_gif


class BaseTest:
    @pytest.fixture
    def dataset(self):
        return Dataset((
            ("s1", "x", 0),
            ("s1", "y", 7),
            ("s2", "x", 4),
            ("s3", "y", 7),
            ("s3", "z", 9),
            ("s4", "x", 4),
        ))


class TestRendering(BaseTest):
    def test_source_positioning(self, dataset):
        source_colour = (0.34, 0.56, 0.78)
        null_colour = (0, 0, 0)

        class ExampleColourScheme(GraphColourScheme):
            def get_node_colour(cself, node_type, _hints):
                if node_type == NodeType.SOURCE:
                    return source_colour, null_colour, null_colour
                return null_colour, null_colour, null_colour

        cs = ExampleColourScheme()
        rend = GraphRenderer(width=100, height=50, colours=cs)
        # rend.render(dataset, None)
        ents = list(rend.compile(dataset))
        assert len(ents) == (
            1        # background
            + 4 * 2  # sources
            + 6      # edges from sources to claims
            + 4 * 2  # claims
            + 4      # edges from claims to variables
            + 3 * 2  # variables
        )

        source_ents = [ent for ent in ents if ent.colour == source_colour]
        assert len(source_ents) == 4
        # Sources should be aligned in x coordinates
        source_coords = [(ent.x, ent.y) for ent in source_ents]
        assert len(set(x for x, y in source_coords)) == 1
        # Check y positioning
        y_coords = sorted(y for x, y in source_coords)
        assert y_coords == [6.25, 18.75, 31.25, 43.75]

    def test_invalid_node_size(self, dataset):
        invalid_sizes = (-1, -0.00001, 0, 1.00001, 10)
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                GraphRenderer(dataset, node_size=size)

    def test_png_is_default(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        rend = GraphRenderer(backend=None)
        assert isinstance(rend.backend, PngBackend)
        rend.render(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

    def test_long_labels(self, tmpdir):
        dataset = Dataset((
            ("a-source-with-an-extremely-long-name", "x", 1000000000000000000),
            ("source 2", "quite a complicated variable name", 100)
        ))
        ents = list(GraphRenderer().compile(dataset))
        assert len(ents) == (
            1 +      # background
            6 * 2 +  # 6 nodes, each represented by two circles
            4        # 4 edges
        )

    def test_matrix_renderer(self):
        buf = BytesIO()
        buf.write(b",5,7\n,,\n1,2,3")
        buf.seek(0)
        dataset = MatrixDataset.from_csv(buf)
        rend1 = MatrixDatasetGraphRenderer()
        rend2 = MatrixDatasetGraphRenderer(zero_indexed=False)

        rend1.render(dataset, BytesIO())
        rend2.render(dataset, BytesIO())

        assert rend1.get_source_label(0) == "s0"
        assert rend2.get_source_label(0) == "s1"
        assert rend1.get_var_label(0) == "v1"
        assert rend2.get_var_label(0) == "v2"

        # Note that source 1 (in 0-index terms) makes no claims: ID 1 should
        # therefore be source 2 (in 0-index terms)
        assert rend1.get_source_label(1) == "s2"
        assert rend2.get_source_label(1) == "s3"

        assert rend1.get_claim_label(0, 1) == "v1=7"
        assert rend2.get_claim_label(0, 1) == "v2=7"


class TestBackends(BaseTest):
    def test_base_backend(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        with pytest.raises(NotImplementedError):
            GraphRenderer(backend=BaseBackend()).render(out, dataset)

    def test_valid_png(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        GraphRenderer(backend=PngBackend()).render(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

    def test_results_based_valid_png(self, dataset, tmpdir):
        cs = ResultsGradientColourScheme(Sums().run(dataset))
        out = tmpdir.join("mygraph.png")
        GraphRenderer(backend=PngBackend(), colours=cs).render(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)


class TestColourSchemes:
    def test_get_gradient_colour(self):
        class Mock(ResultsGradientColourScheme):
            COLOURS = [1, 2, 3, 4]

        colour_scheme = Mock(None)
        test_cases = [
            # (level, expected index)
            (0, 0),
            (0.2, 0),
            (0.24999, 0),
            (0.25, 1),
            (0.49999, 1),
            (0.5, 2),
            (0.6, 2),
            (0.74999, 2),
            (0.75, 3),
            (0.999, 3),
            (1, 3)
        ]
        for level, exp_index in test_cases:
            colour, _ = colour_scheme.get_graded_colours(level)
            assert colour == colour_scheme.COLOURS[exp_index]

    def test_plain_colour_scheme(self):
        cs = PlainColourScheme()
        source = cs.get_node_colour(NodeType.SOURCE, 0)
        var = cs.get_node_colour(NodeType.VARIABLE, 0)
        claim = cs.get_node_colour(NodeType.CLAIM, 0, 0)
        # All nodes types should have the same colours in the plain theme
        assert source == var == claim
        # Label and border should be the same colour
        assert source[1] == source[2]
        # Edges should be the same colour as node borders
        edge = cs.get_edge_colour()
        assert edge == source[2]
        # Background should be the same as node interiors
        background = cs.get_background_colour()
        assert background == source[0]

    def test_results_based_colours(self):
        results = Result(
            trust={"s1": 0, "s2": 0.01, "s3": 0.6, "s4": 1},
            belief={"x": {1: 0, 2: 0.34, 3: 0.7, 4: 1}},
            time_taken=None
        )
        colour_scheme = ResultsGradientColourScheme(results)
        n_s1, l_s1, _ = colour_scheme.get_node_colour(NodeType.SOURCE, "s1")
        n_s2, l_s2, _ = colour_scheme.get_node_colour(NodeType.SOURCE, "s2")
        n_s3, l_s3, _ = colour_scheme.get_node_colour(NodeType.SOURCE, "s3")
        n_s4, l_s4, _ = colour_scheme.get_node_colour(NodeType.SOURCE, "s4")

        assert n_s1 == n_s2
        assert l_s1 == l_s2
        assert l_s1 != l_s3
        assert l_s3 == l_s4

        claim_type = NodeType.CLAIM
        n_c1, l_c1, _ = colour_scheme.get_node_colour(claim_type, ("x", 1))
        n_c2, l_c2, _ = colour_scheme.get_node_colour(claim_type, ("x", 2))
        n_c3, l_c3, _ = colour_scheme.get_node_colour(claim_type, ("x", 3))
        n_c4, l_c4, _ = colour_scheme.get_node_colour(claim_type, ("x", 4))

        assert l_c1 == l_c2
        assert l_c1 != l_c3
        assert l_c3 == l_c4


class TestAnimations(BaseTest):
    def test_valid_gif(self, dataset):
        w, h = 123, 78
        renderer = GraphRenderer(width=w, height=h)
        animator = Animator(renderer=renderer)
        alg = Sums()
        buf = BytesIO()
        animator.animate(buf, alg, dataset)
        buf.seek(0)
        assert is_valid_gif(buf)

        # Check dimensions are as expected
        buf.seek(0)
        img_data = imageio.imread(buf)
        got_w, got_h, _ = img_data.shape
        assert (got_h, got_w) == (w, h)

    def test_renderer(self):
        # Custom renderer should be used if provided
        custom_renderer = GraphRenderer(font_size=10000)
        anim = Animator(renderer=custom_renderer)
        assert anim.renderer == custom_renderer

        # Otherwise a default renderer
        anim2 = Animator()
        assert isinstance(anim2.renderer, GraphRenderer)

    def test_fps(self):
        anim = Animator(frame_duration=1 / 3)
        assert anim.fps == 3
