from io import BytesIO
import imageio
import pytest

from truthdiscovery.algorithm import Sums
from truthdiscovery.input import Dataset, MatrixDataset
from truthdiscovery.output import Result
from truthdiscovery.graphs import (
    Animator,
    GraphRenderer,
    MatrixDatasetGraphRenderer,
    NodeType,
    PlainColourScheme,
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


class TestDrawing(BaseTest):
    @pytest.fixture
    def mock_renderer_cls(self):
        class Mock(GraphRenderer):
            draw_calls = []

            def _log(m_self, args, kwargs):
                m_self.draw_calls.append((args, kwargs))

            def draw_node(m_self, *args, **kwargs):
                m_self._log(args, kwargs)

            def draw_edge(m_self, *args, **kwargs):
                m_self._log(args, kwargs)

            def write_to_file(m_self, *args, **kwargs):
                pass

        return Mock

    def test_source_positioning(self, dataset, mock_renderer_cls):
        rend = mock_renderer_cls(width=100, height=50)
        rend.draw(dataset, None)
        assert len(rend.draw_calls) == (
            4    # sources
            + 6  # edges from sources to claims
            + 4  # claims
            + 4  # edges from claims to variables
            + 3  # variables
        )

        source_calls = rend.draw_calls[-4:]
        # Sources should be aligned in x coordinates
        source_coords = [args[2] for args, kwargs in source_calls]
        assert len(set(x for x, y in source_coords)) == 1
        # Check y positioning
        y_coords = sorted(y for x, y in source_coords)
        assert y_coords == [6.25, 18.75, 31.25, 43.75]

    def test_invalid_node_size(self, dataset):
        invalid_sizes = (-1, -0.00001, 0, 1.00001, 10)
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                rend = GraphRenderer(dataset, node_size=size)

    def test_valid_png(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        GraphRenderer().draw(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

    def test_long_labels(self, tmpdir):
        dataset = Dataset((
            ("a-source-with-an-extremely-long-name", "x", 1000000000000000000),
            ("source 2", "quite a complicated variable name", 100)
        ))
        out = tmpdir.join("mygraph.png")
        GraphRenderer().draw(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

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
            print(level)
            colour, _ = colour_scheme.get_graded_colours(level)
            assert colour == colour_scheme.COLOURS[exp_index]

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

    def test_results_based_valid_png(self, dataset, tmpdir):
        cs = ResultsGradientColourScheme(Sums().run(dataset))
        out = tmpdir.join("mygraph.png")
        GraphRenderer(colours=cs).draw(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

    def test_matrix_renderer(self):
        buf = BytesIO()
        buf.write(b",5,7\n1,2,3")
        buf.seek(0)
        dataset = MatrixDataset.from_csv(buf)
        rend1 = MatrixDatasetGraphRenderer()
        rend2 = MatrixDatasetGraphRenderer(zero_indexed=False)

        rend1.draw(dataset, BytesIO())
        rend2.draw(dataset, BytesIO())

        assert rend1.get_source_label(0) == "s0"
        assert rend2.get_source_label(0) == "s1"
        assert rend1.get_var_label(0) == "v0"
        assert rend2.get_var_label(0) == "v1"

        assert rend1.get_claim_label(0, 1) == "v0=7"
        assert rend2.get_claim_label(0, 1) == "v1=7"

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


class TestAnimations(BaseTest):
    def test_valid_gif(self, dataset):
        w, h = 123, 78
        renderer = GraphRenderer(width=w, height=h)
        animator = Animator(renderer=renderer)
        alg = Sums()
        buf = BytesIO()
        animator.animate(buf, alg, dataset)
        buf.seek(0)
        print(buf.read(8))
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
