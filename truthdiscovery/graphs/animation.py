from io import BytesIO, StringIO
import json

import imageio

from truthdiscovery.graphs.backends import JsonBackend, PngBackend
from truthdiscovery.graphs.colours import ResultsGradientColourScheme
from truthdiscovery.graphs.draw import GraphRenderer


class BaseAnimator:
    """
    Base class to handle creating an animation of results-coloured graphs over
    the course of an algorithm's iteration.
    """
    # Must be defined in child classes
    buffer_cls = None
    supported_backends = ()

    def __init__(self, renderer=None, frame_duration=0.2):
        """
        :param renderer:       :any:`GraphRenderer` (or sub-class) object, or
                               None to use a default renderer
        :param frame_duration: duration in seconds for each frame
        """
        if renderer is None:
            default_backend_cls = self.supported_backends[0]
            renderer = GraphRenderer(backend=default_backend_cls())
        self.renderer = renderer
        self.fps = 1 / frame_duration

        if not isinstance(self.renderer.backend, self.supported_backends):
            clses = ", ".join(cls.__name__ for cls in self.supported_backends)
            raise TypeError(
                "Invalid renderer backend type {}, must be one of: {}"
                .format(self.renderer.backend.__class__, clses)
            )

    def animate(self, outfile, algorithm, dataset):
        """
        :param outfile:   file object to write to
        :param algorithm: :any:`BaseIterativeAlgorithm` sub-class instance
        :param dataset:   :any:`Dataset` object
        """
        frames = self.get_frames(algorithm, dataset)
        self.write(frames, outfile)

    def get_frames(self, algorithm, dataset):
        """
        A generator of ``buffer_cls`` objects for each frame in the animation
        """
        # Note: must collect all results so we can get total number of
        # iterations to work out completion percentage at each step
        all_results = tuple(algorithm.run_iter(dataset))
        num_iterations = len(all_results)

        for i, results in enumerate(all_results):
            self.renderer.colours = ResultsGradientColourScheme(results)
            # Draw frame to in-memory buffer
            buf = self.buffer_cls()
            progress = i / num_iterations
            self.renderer.render(dataset, buf, animation_progress=progress)
            buf.seek(0)
            yield buf

    def write(self, frames, outfile):
        """
        :param frames:  iterable of frames as ``buffer_cls`` instances
        :param outfile: file object to write to
        """
        raise NotImplementedError("Must be implemented in child classes")


class GifAnimator(BaseAnimator):
    """
    Create an animation as a GIF. Must be used with a renderer with PNG backend
    """
    buffer_cls = BytesIO
    supported_backends = (PngBackend,)

    def write(self, frames, outfile):
        kwargs = dict(format="gif", mode="I", fps=self.fps)
        with imageio.get_writer(outfile, **kwargs) as writer:
            for buf in frames:
                writer.append_data(imageio.imread(buf))


class JsonAnimator(BaseAnimator):
    """
    Create a JSON object containing each frame of the animation
    """
    buffer_cls = StringIO
    supported_backends = (JsonBackend,)

    def write(self, frames, outfile):
        obj = {"fps": self.fps, "frames": [json.load(buf) for buf in frames]}
        json.dump(obj, outfile)
