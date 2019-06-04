import unittest
import numpy as np
from src.AnimatedFigureQt import AnimatedFigure as AnimFigQt
from src.AnimatedFigure import AnimatedFigure as AnimFigMpl


maxpoints = int(200)   # Plot up to 200 points


class TestQt(unittest.TestCase):
    """
    This is really a functional test.
    TODO: work on making AnimatedFigure more modular and write some real unit tests.
    """

    def testMPL(self):
        for num_plots in [1, 5, 10]:
            for num_y in [1, 5, 10]:
                for plot_samples in [2, 50, 100]:
                    for interval in [1, 5, 25]:
                        with self.subTest(name=f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}"):
                            print("Working on: " + f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}")
                            x = []
                            y = []
                            self.an = AnimFigMpl(lambda i: return_multi(i=i, num_y=num_y, num_plots=num_plots,
                                                                        x=x, y=y),
                                                 plot_samples=plot_samples, interval=interval)
                            self.an.animate()
                            del self.an, x, y

    def testQt(self):
        for num_plots in [1, 5, 10]:
            for num_y in [1, 5, 10]:
                for plot_samples in [2, 50, 100]:
                    for interval in [1, 5, 25]:
                        with self.subTest(name=f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}"):
                            print("Working on: " + f"num_plots: {num_plots}, num_y: {num_y}, plot_samples: {plot_samples}, interval: {interval}")
                            x = []
                            y = []
                            self.an = AnimFigQt(lambda i: return_multi(i=i, num_y=num_y, num_plots=num_plots, x=x, y=y),
                                                plot_samples=plot_samples, interval=interval)
                            self.an.animate()
                            del self.an, x, y


def return_multi(i, x, y, num_y=1, num_plots=1):
    if i > maxpoints:
        raise StopIteration
    x.append(i / 100 * 2 * np.pi)
    y.append(np.cos(x[-1]))
    return list((tuple([np.array(x)] + [np.array(y) ** power for power in range(1, num_y + 1)]), ) * num_plots)


if __name__ == '__main__':
    unittest.main()
