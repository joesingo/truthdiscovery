import pytest

from truthdiscovery.input import Dataset
from truthdiscovery.visual import GraphRenderer


class TestDrawing:
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
        rend = mock_renderer_cls(dataset, width=100, height=50)
        rend.draw(None)
        assert len(rend.draw_calls) == (
            4    # sources
            + 6  # edges from sources to claims
            + 4  # claims
            + 4  # edges from claims to variables
            + 3  # variables
        )

        source_calls = rend.draw_calls[-4:]
        # Sources should be aligned in x coordinates
        source_coords = [args[-1] for args, kwargs in source_calls]
        assert len(set(x for x, y in source_coords)) == 1
        # Check y positioning
        y_coords = sorted(y for x, y in source_coords)
        assert y_coords == [6.25, 18.75, 31.25, 43.75]

    def test_valid_png(self, dataset, tmpdir):
        out = tmpdir.join("mygraph.png")
        GraphRenderer(dataset).draw(out)
        with open(str(out), "rb") as f:
            signature = f.read(8)
        assert signature == b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
