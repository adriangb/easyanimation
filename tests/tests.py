import unittest
import numpy as np
from collections import deque
from itertools import islice

from src.AnimatedFigureQt import AnimatedFigure as AnimFigQt
from src.AnimatedFigure import AnimatedFigure as AnimFigMpl
from src.data_slicer import data_slicer

frameworks = (AnimFigQt, AnimFigMpl)


class TestSlice(unittest.TestCase):

    maxpoints = int(1000)  # Slice up to 1000 points
    x = [i / 100 * 2 * np.pi for i in range(maxpoints)]
    y = list(np.cos(x))

    def test_lengths(self):
        for num_plots in [1, 5, 10]:
            for num_y in [1, 5, 10]:
                for plot_samples in [2, 50, 100]:
                    for i in range(2, plot_samples * 2):
                        with self.subTest(name=f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}"):
                            print(f"Working on {data_slicer.__module__}: " +
                                  f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}")
                            for (x, *y_points) in return_multi(i=i, num_y=num_y, num_plots=num_plots, x=self.x, y=self.y, maxpoints=self.maxpoints):
                                x_sliced, y_data_sliced = data_slicer(plot_samples, x, y_points)
                                for y in y_data_sliced:
                                    self.assertTrue(len(x_sliced) == len(y) == plot_samples, "Slicing produced unexpected lengths")

class TestRescale(unittest.TestCase):

    maxpoints = int(1000)  # Slice up to 1000 points
    x = [i / 100 * 2 * np.pi for i in range(maxpoints)]
    y = list(np.cos(x))

    def test_x(self):
        # TODO: Implement testing for x-axis rescaling in MPL backend only
        pass
    def test_y(self):
        # TODO: Implement testing for y-axis rescaling in MPL backend only
        pass


class TestQt(unittest.TestCase):
    """
    This is really a functional test.
    TODO: work on making AnimatedFigure more modular and write some real unit tests.
    """
    maxpoints = int(200)  # Plot up to 200 points
    x = [i / 100 * 2 * np.pi for i in range(maxpoints)]
    y = list(np.cos(x))
    test_data = ((x, y), (np.array(x), np.array(y)), (deque(x), deque(y)))

    def testMPL(self):
        for num_plots in [1, 5, 10]:
            for num_y in [1, 5, 10]:
                for plot_samples in [2, 50, 100]:
                    for interval in [1, 5, 25]:
                        for (x, y) in self.test_data:
                            for framework in frameworks:
                                with self.subTest(name=f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}"):
                                    print(f"Working on {framework.__module__}: " + f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}")
                                    self.an = framework(lambda i: return_multi(i=i, num_y=num_y, num_plots=num_plots, x=x, y=y, maxpoints=self.maxpoints), plot_samples=plot_samples, interval=interval)
                                    self.an.animate()
                                    del self.an


def return_multi(i, x, y, num_y, num_plots, maxpoints):
    if i > maxpoints:
        raise StopIteration
    try:
        x = x[:i]
        y = y[:i]
        return tuple((tuple([x]) + tuple([point ** power for point in y] for power in range(1, num_y + 1)), ) * num_plots)
    except TypeError:
        x = list(islice(x, 0, i, 1))
        y = list(islice(x, 0, i, 1))
        return tuple((tuple([deque(x)]) + tuple(deque([point ** power for point in y]) for power in range(1, num_y + 1)), ) * num_plots)


if __name__ == '__main__':
    unittest.main()
