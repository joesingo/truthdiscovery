from io import BytesIO

import imageio

from truthdiscovery.graphs.colours import ResultsGradientColourScheme
from truthdiscovery.graphs.draw import GraphRenderer


class Animator:
    """
    Object to handle creating an animated GIF of results-coloured graphs over
    the course of an algorithm's iteration
    """

    def __init__(self, renderer=None, frame_duration=0.2):
        """
        :param renderer:       :any:`GraphRenderer` (or sub-class) object, or
                               None to use a default renderer
        :param frame_duration: duration in seconds for each frame
        """
        self.renderer = renderer or GraphRenderer()
        self.fps = 1 / frame_duration

    def animate(self, outfile, algorithm, dataset):
        """
        :param outfile:   file object to write to
        :param algorithm: :any:`BaseIterativeAlgorithm` sub-class instance
        :param dataset:   :any:`Dataset` object
        """
        kwargs = dict(format="gif", mode="I", fps=self.fps)
        with imageio.get_writer(outfile, **kwargs) as writer:
            # Note: must collect all results so we can get total number of
            # iterations to work out completion percentage at each step
            all_results = tuple(algorithm.run_iter(dataset))
            num_iterations = len(all_results)

            for i, results in enumerate(all_results):
                self.renderer.colours = ResultsGradientColourScheme(results)
                # Draw frame to in-memory buffer
                imgbuf = BytesIO()
                self.renderer.draw(
                    dataset, imgbuf,
                    animation_progress=i / num_iterations
                )
                imgbuf.seek(0)
                writer.append_data(imageio.imread(imgbuf))
