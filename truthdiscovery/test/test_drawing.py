from io import BytesIO, StringIO
import json
from operator import attrgetter

import imageio
import pytest

from truthdiscovery.algorithm import Sums
from truthdiscovery.input import Dataset, MatrixDataset
from truthdiscovery.output import Result
from truthdiscovery.graphs import (
    BaseAnimator,
    BaseBackend,
    Circle,
    GifAnimator,
    GraphColourScheme,
    GraphRenderer,
    JsonAnimator,
    JsonBackend,
    Label,
    Line,
    MatrixDatasetGraphRenderer,
    NodeType,
    PlainColourScheme,
    PngBackend,
    Rectangle,
    ResultsGradientColourScheme,
)
from truthdiscovery.utils import FixedIterator
from truthdiscovery.test.utils import is_valid_png, is_valid_gif


class ExampleColourScheme(GraphColourScheme):
    colours = {
        NodeType.SOURCE: (0.1, 0.1, 0.1),
        NodeType.CLAIM: (0.2, 0.2, 0.2),
        NodeType.VARIABLE: (0.3, 0.3, 0.3),
        "edge": (0.4, 0.4, 0.4),
        "label": (0.5, 0.5, 0.5),
        "border": (0.6, 0.6, 0.6),
        "background": (0.7, 0.7, 0.7)
    }

    def get_node_colour(self, node_type, _hints):
        cs = self.colours
        return cs[node_type], cs["label"], cs["border"]

    def get_background_colour(self):
        return self.colours["background"]

    def get_edge_colour(self):
        return self.colours["edge"]


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
    def test_entity_positioning(self, dataset):
        cs = ExampleColourScheme()
        rend = GraphRenderer(width=100, height=50, colours=cs)
        ents = list(rend.compile(dataset))

        assert len(ents) == (
            1        # background
            + 4 * 2  # sources
            + 6      # edges from sources to claims
            + 4 * 2  # claims
            + 4      # edges from claims to variables
            + 3 * 2  # variables
        )

        colours = ExampleColourScheme.colours
        bgs = [e for e in ents if e.colour == colours["background"]]
        assert len(bgs) == 1
        assert isinstance(bgs[0], Rectangle)
        assert bgs[0].x == 0
        assert bgs[0].y == 0
        assert bgs[0].width == 100
        assert bgs[0].height == 50

        # Should be 4 sources, 4 claims, and 3 variables
        source_ents = [e for e in ents if e.colour == colours[NodeType.SOURCE]]
        claim_ents = [e for e in ents if e.colour == colours[NodeType.CLAIM]]
        var_ents = [e for e in ents if e.colour == colours[NodeType.VARIABLE]]
        for e in source_ents:
            print(e.x, e.y, e.colour)
        assert len(source_ents) == 4
        assert len(claim_ents) == 4
        assert len(var_ents) == 3

        # Should be 4 + 4 + 3 border circles
        border_ents = [e for e in ents if e.colour == colours["border"]]
        assert len(border_ents) == 4 + 4 + 3

        # All nodes should be Circle objects
        for e in source_ents + claim_ents + var_ents + border_ents:
            assert isinstance(e, Circle)

        # There should be 6 edges from sources to claims, and 4 from claims to
        # variables
        edge_ents = [e for e in ents if e.colour == colours["edge"]]
        assert len(edge_ents) == 6 + 4
        for e in edge_ents:
            assert isinstance(e, Line)

        # Sources should be aligned in x coordinates
        source_coords = [(ent.x, ent.y) for ent in source_ents]
        assert len(set(x for x, y in source_coords)) == 1
        # Check y positioning
        y_coords = sorted(y for x, y in source_coords)
        assert y_coords == [6.25, 18.75, 31.25, 43.75]

    def test_node_ordering(self):
        # Construct a dataset where claim tuples are not sorted by source,
        # variable or value
        dataset = Dataset((
            ("source 4", "z", 9),
            ("source 3", "x", 4),
            ("source 1", "x", 1),
            ("source 1", "y", 2),
            ("source 2", "x", 6),
            ("source 2", "z", 3)
        ))

        # Claims should be sorted first by their variable's label, and then by
        # their own label. Change the default claim label method so that we can
        # distinguish between the correct behaviour and when the claims are
        # incorrectly sorted only by their own labels.
        class ExampleGraphRenderer(GraphRenderer):
            def get_claim_label(rend_self, var_id, val_hash):
                return "{val} = {var}".format(
                    val=rend_self.dataset.val_hashes.inverse[val_hash],
                    var=rend_self.dataset.var_ids.inverse[var_id]
                )

        rend = ExampleGraphRenderer(colours=ExampleColourScheme())
        ents = list(rend.compile(dataset))

        c = ExampleColourScheme.colours
        source_ls = [e.label for e in ents if e.colour == c[NodeType.SOURCE]]
        var_ls = [e.label for e in ents if e.colour == c[NodeType.VARIABLE]]
        claim_ls = [e.label for e in ents if e.colour == c[NodeType.CLAIM]]

        source_ls.sort(key=attrgetter("y"))
        var_ls.sort(key=attrgetter("y"))
        claim_ls.sort(key=attrgetter("y"))

        sorted_sources = [l.text for l in source_ls]
        sorted_vars = [l.text for l in var_ls]
        sorted_claims = [l.text for l in claim_ls]

        assert sorted_sources == [
            "source 1", "source 2", "source 3", "source 4"
        ]
        assert sorted_vars == ["x", "y", "z"]
        assert sorted_claims == [
            "1 = x", "4 = x", "6 = x",
            "2 = y",
            "3 = z", "9 = z"
        ]

    def test_single_source(self):
        one_source_dataset = Dataset((
            ("source 1", "x", 1),
            ("source 1", "y", 1)
        ))
        one_var_dataset = Dataset((
            ("source 1", "x", 1),
            ("source 2", "x", 2)
        ))
        one_claim_dataset = Dataset((
            ("source 1", "x", 1),
            ("source 2", "x", 1)
        ))
        rend = GraphRenderer(colours=ExampleColourScheme())
        # Check the positioning of nodes for the one-source dataset
        ents = list(rend.compile(one_source_dataset))
        colours = ExampleColourScheme.colours
        sources = [e for e in ents if e.colour == colours[NodeType.SOURCE]]
        assert len(sources) == 1
        assert sources[0].y == rend.height / 2
        # Check the other two don't raise any exceptions
        list(rend.compile(one_var_dataset))
        list(rend.compile(one_claim_dataset))

    def test_invalid_node_size(self, dataset):
        invalid_sizes = (-1, -0.00001, 0, 1.00001, 10)
        for size in invalid_sizes:
            with pytest.raises(ValueError):
                GraphRenderer(dataset, node_size=size)

    def test_no_horizontal_overlapping(self):
        dataset = Dataset([("source 1", "x", 100)])
        size = 30
        rend = GraphRenderer(
            colours=ExampleColourScheme(), width=size, height=size, node_size=1
        )
        ents = list(rend.compile(dataset))
        colours = ExampleColourScheme.colours
        nodes = [e for e in ents if e.colour == colours["border"]]
        assert len(nodes) == 3
        radii = {e.radius for e in nodes}
        assert len(radii) == 1
        assert list(radii)[0] == size / 6

    def test_png_is_default(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        rend = GraphRenderer(backend=None)
        assert isinstance(rend.backend, PngBackend)
        rend.render(dataset, out)
        with open(str(out), "rb") as f:
            assert is_valid_png(f)

    def test_long_labels(self):
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
        buf = StringIO()
        buf.write(",5,7\n,,\n1,2,3")
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

    def test_image_size(self, dataset):
        buf = BytesIO()
        w = 142
        h = 512
        rend = GraphRenderer(width=w, height=h, backend=PngBackend())
        rend.render(dataset, buf)
        buf.seek(0)
        img_data = imageio.imread(buf)
        got_w, got_h, _ = img_data.shape
        assert (got_h, got_w) == (w, h)

    def test_progress_bar(self, dataset):
        w = 200
        h = 512
        anim_colour = (0.34, 0.99, 0.34)

        class MyColourScheme(GraphColourScheme):
            def get_animation_progress_colour(self):
                return anim_colour

        rend = GraphRenderer(width=w, height=h, colours=MyColourScheme())
        ents = list(rend.compile(dataset, animation_progress=0.25))
        rects = [e for e in ents if e.colour == anim_colour]
        assert len(rects) == 1
        assert rects[0].x == 0
        assert rects[0].width == 50

        # Test without progress bar
        ents2 = list(rend.compile(dataset, animation_progress=None))
        rects2 = [e for e in ents2 if e.colour == anim_colour]
        assert not len(rects2)


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

    def test_json_backend(self):
        w = 123
        h = 456
        rend = GraphRenderer(width=w, height=h, backend=JsonBackend())
        buf = StringIO()

        data = Dataset((
            ("s1", "x", 0),
            ("s2", "y", 1)
        ))

        rend.render(data, buf)
        buf.seek(0)
        obj = json.load(buf)
        assert isinstance(obj, dict)
        assert "width" in obj
        assert "height" in obj
        assert "entities" in obj
        assert obj["width"] == w
        assert obj["height"] == h

        ents = obj["entities"]
        assert isinstance(ents, list)
        assert len(ents) == (
            1        # background
            + 6 * 2  # 6 nodes
            + 4      # 4 edges
        )
        assert ents[0] == {
            "type": "rectangle",
            "x": 0,
            "y": 0,
            "colour": list(rend.colours.get_background_colour()),
            "width": w,
            "height": h
        }

    def test_json_backend_entity_serialisation(self):
        rect = Rectangle(x=1, y=2, colour=(0.5, 0.6, 0.7), width=10, height=20)
        assert JsonBackend.entity_to_dict(rect) == {
            "type": "rectangle",
            "x": 1,
            "y": 2,
            "colour": (0.5, 0.6, 0.7),
            "width": 10,
            "height": 20
        }
        circ = Circle(x=1, y=2, colour=(0.5, 0.6, 0.7), radius=11)
        assert JsonBackend.entity_to_dict(circ) == {
            "type": "circle",
            "x": 1,
            "y": 2,
            "colour": (0.5, 0.6, 0.7),
            "radius": 11,
            "label": None
        }
        line = Line(
            x=1, y=2, colour=(0.5, 0.6, 0.7), end_x=10, end_y=100, width=202
        )
        assert JsonBackend.entity_to_dict(line) == {
            "type": "line",
            "x": 1,
            "y": 2,
            "colour": (0.5, 0.6, 0.7),
            "end_x": 10,
            "end_y": 100,
            "width": 202
        }
        label = Label(
            x=1, y=2, colour=(0.1, 0.4, 0.9), text="hello", size=123,
            overflow_background=(0.9, 0.4, 0.1)
        )
        assert JsonBackend.entity_to_dict(label) == {
            "type": "label",
            "x": 1,
            "y": 2,
            "colour": (0.1, 0.4, 0.9),
            "text": "hello",
            "size": 123,
            "overflow_background": (0.9, 0.4, 0.1)
        }
        cirl_with_label = Circle(
            x=1, y=2, colour=(0.5, 0.6, 0.7), radius=11, label=label
        )
        assert JsonBackend.entity_to_dict(cirl_with_label) == {
            "type": "circle",
            "x": 1,
            "y": 2,
            "colour": (0.5, 0.6, 0.7),
            "radius": 11,
            "label": JsonBackend.entity_to_dict(label)
        }


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
        # Background should be transparent
        background = cs.get_background_colour()
        assert background[3] == 0

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
    def test_base(self, dataset):
        class MyAnimator(BaseAnimator):
            supported_backends = (PngBackend,)

        with pytest.raises(NotImplementedError):
            MyAnimator().animate(BytesIO(), Sums(), dataset)

    def test_gif_animation(self, dataset):
        w, h = 123, 78
        renderer = GraphRenderer(width=w, height=h)
        animator = GifAnimator(renderer=renderer)
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

    def test_json_animation(self, dataset):
        w, h = 123, 78
        renderer = GraphRenderer(width=w, height=h, backend=JsonBackend())
        animator = JsonAnimator(renderer=renderer, frame_duration=1 / 9)
        alg = Sums(iterator=FixedIterator(4))
        buf = StringIO()
        animator.animate(buf, alg, dataset)
        buf.seek(0)
        obj = json.load(buf)

        assert "fps" in obj
        assert obj["fps"] == 9
        assert "frames" in obj
        assert isinstance(obj["frames"], list)
        assert len(obj["frames"]) == 5
        assert isinstance(obj["frames"][0], dict)
        assert "width" in obj["frames"][0]
        assert "height" in obj["frames"][0]
        assert "entities" in obj["frames"][0]
        assert obj["frames"][0]["width"] == w
        assert obj["frames"][0]["height"] == h

    def test_renderer(self):
        # Custom renderer should be used if provided
        custom_renderer = GraphRenderer(font_size=10000)
        anim = GifAnimator(renderer=custom_renderer)
        assert anim.renderer == custom_renderer

        # Otherwise a default renderer
        anim2 = GifAnimator()
        assert isinstance(anim2.renderer, GraphRenderer)

    def test_fps(self):
        anim = GifAnimator(frame_duration=1 / 3)
        assert anim.fps == 3

    def test_invalid_backend(self):
        png_rend = GraphRenderer(backend=PngBackend())
        json_rend = GraphRenderer(backend=JsonBackend())
        with pytest.raises(TypeError):
            GifAnimator(renderer=json_rend)
        with pytest.raises(TypeError):
            JsonAnimator(renderer=png_rend)

    def test_default_backend(self):
        class SomeClass:
            pass

        class MyAnimator(BaseAnimator):
            supported_backends = (SomeClass, float, int)

        anim = MyAnimator()
        assert isinstance(anim.renderer.backend, SomeClass)

    def test_progress_bar(self, dataset):
        w = 200
        h = 200
        rend = GraphRenderer(width=w, height=h, backend=JsonBackend())
        anim = JsonAnimator(renderer=rend)

        buf = StringIO()
        it = FixedIterator(20)
        alg = Sums(iterator=it)
        anim.animate(buf, alg, dataset, show_progress=True)
        buf.seek(0)
        obj = json.load(buf)
        # Get the frame for the 5th iteration, which is 1 / 4 through
        frame = obj["frames"][5]
        rects = [
            e for e in frame["entities"]
            if e["type"] == "rectangle" and e["width"] != w
        ]
        assert len(rects) == 1
        assert rects[0]["x"] == 0
        assert rects[0]["width"] == w / 4

        # Test without progress
        buf2 = StringIO()
        anim.animate(buf2, alg, dataset, show_progress=False)
        buf2.seek(0)
        obj2 = json.load(buf2)
        frame2 = obj2["frames"][5]
        rects2 = [
            e for e in frame2["entities"]
            if e["type"] == "rectangle" and e["width"] != w
        ]
        assert not len(rects2)
