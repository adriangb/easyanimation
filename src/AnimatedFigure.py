# Set backend
import matplotlib

# Imports
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
import itertools
import time

from .data_slicer import data_slicer


class AnimatedFigure:

    def __init__(self, data_function, plot_samples, interval=1, debug=False):
        """
        Initializes the live-plots and starts polling for new data.
        If you want to edit the axis titles and such, instantiate the class then acess the self.axes object.
        :param data_function: a generator function which returns the plotting data whenever it is called.
        Remeber, in Python functions are first class!
        :param plot_samples: initial batch of data to be plotted. Refer to update_plots() for info on data format.
        :param interval: interval (in ms) between polling to data_function().
        Increase to reduce resource utilization at the cost of smoothness. Recommend setting to sampling freq of data.
        :param debug: prints FPS at which plot is rendered.
        :return: animated plot object.
        """
        # counter vars for performance monitoring
        self.counter = 0
        self.debug = debug
        # initialize figure
        self.interval = interval
        self.data_function = data_function
        init_data = self.data_function(0)
        self.num_plots = len(init_data)
        try:
            if len(plot_samples) > 1:
                assert self.num_plots == len(plot_samples), \
                    f"Size of plot_samples is {len(plot_samples)} while data_function signature is {self.num_plots}."
                assert all([True if plot_sample > 1 else False for plot_sample in plot_samples]), "plot_samples must be >1"
                self.plot_samples = plot_samples
        except TypeError:
            self.plot_samples = [plot_samples for _ in range(self.num_plots)]
        # make copies to avoid overwriting mutable objects
        initial_plot_data = []
        for xy_data, plot_samples in zip(init_data, self.plot_samples):
            sublist = []
            for _ in xy_data[1:]:
                new_line = np.zeros(plot_samples)
                sublist.append(new_line)
            initial_plot_data.append(sublist)
        # Switch backends
        try:
            self.original_backend = matplotlib.get_backend()
            # Switch graphics backend to TkAgg to be able to function in IPython
            matplotlib.use('TkAgg')
        except:
            print("Unable to load TkAgg.")
            print("If using Spyder: Please to go to Tools > Preferences > IPython Console > Graphics and change Backend to \"Tkinter\"")
            raise

        self.fig = plt.figure()
        self.axes = self.fig.subplots(1, self.num_plots, squeeze=False)[0]
        self.fig.canvas.mpl_connect('close_event', self.stop)
        try:
            self.fig.canvas._master.report_callback_exception = self.exception_handler
        except AttributeError:
            print("Could not connect plot close callback")
        self.live_plot = []
        for ax, y_data in zip(self.axes, initial_plot_data):
            sublist = []
            for y in y_data:
                new_line = ax.plot(y)[0]
                sublist.append(new_line)
            self.live_plot.append(sublist)
        plt.tight_layout()
        self.ani = None  # placeholder for animation object
        self.timer = time.time()

    def _update_x_labels(self, ax, x, plot_samples):
        """
        Rescale/relabel x axis.
        Number and location of ticks is left to be auto determined, we just change the labels.
        :param ax: axis object to updated x axis labels on.
        :param x: iterable containing current x data. Must be of length plot_samples or greater.
        :param plot_samples: number of data points that the axis is displaying.
        :return: boolean indicating if redraw is necessary.
        """
        # If there are enough x-data points, update the x-axis labels
        if len(x) >= plot_samples:
            x_ticks = ax.get_xticks()
            x_tick_labels = [item.get_text() for item in ax.get_xticklabels() if len(item.get_text()) > 0]
            new_labels = [float(f'{x:1.1}') for x in x_ticks / plot_samples * (x[-1] - x[-plot_samples])]
            if new_labels[0] != float(x_tick_labels[0].replace(u'\u2212', '-'))\
                    or new_labels[-1] != float(x_tick_labels[-1].replace(u'\u2212', '-')):
                ax.set_xticklabels(new_labels)
                return True
        return False

    def _update_y_labels(self, ax, y_points):
        """
        Rescale/relabel y axis. We don't use auto-scaling since that can cause hysteresis and unnecessary draws.
        :param y_data: aggregate of all y data on plat (i.e. join all y data)
        :return: boolean indicating if redraw is necessary.
        """
        old_ymin, old_ymax = ax.get_ylim()
        new_min_lim, new_max_lim = self._calc_y_labels(y_points)
        if not ((.85 < old_ymax / new_max_lim < 1.15) and (.85 < old_ymin / new_min_lim < 1.15)):
            ax.set_ylim(bottom=new_min_lim, top=new_max_lim)
            return True
        return False

    def _calc_y_labels(self, y_points):
        # check if data is out of range of axis, if so force y-axis to update
        y_valid = np.array([val for val in [y_point for y_list in y_points for y_point in y_list]
                            if val is not None and not np.isnan(val)])
        if len(y_valid) >= 2:
            data_min, data_max = np.min(y_valid), np.max(y_valid)
            data_range = data_max - data_min
            new_max_lim = data_max + data_range * 0.1
            new_min_lim = data_min - data_range * 0.1
        else:
            new_min_lim = new_max_lim = np.average(y_valid)

        if new_max_lim == new_min_lim:
            new_max_lim = new_max_lim + .1  # ensures if the line is constant axis are still scaled
            new_min_lim = new_max_lim - .1  # ensures if the line is constant axis are still scaled

        return new_min_lim, new_max_lim

    def update_plots(self, idx):
        """
        Updates the live-plots based on new data collected.
        A maximum of plot_samples data points will be plotted.
        Axis limits are automatically adjusted.
        :param idx: required parameter by FuncAnimation. It is not used.
        :return: list of objects (axis) updated.
        """

        self.fps()

        redraw = False

        try:
            data = self.data_function(idx)  # data_function must return a tuple containing lists of x,y data
        except StopIteration:
            self.stop(None)
            raise

        for plot_num, (ax, plot_samples, (x, *y_points)) in enumerate(zip(self.axes, self.plot_samples, data)):
            x, y_points = data_slicer(plot_samples, x, y_points)
            # This way we can accept any iterable as y
            for line, y in zip(self.live_plot[plot_num], y_points):
                line.set_ydata(y)

            if idx % (plot_samples / 2) == 0 and idx > 5:
                # Only check every couple frames for speed
                # Labels will not update properly on the first couple frames, skip them
                if self._update_y_labels(ax, y_points) or self._update_x_labels(ax, x, plot_samples):
                    redraw = True
        if redraw:
            self.fig.canvas.draw_idle()

        return [line for plot in self.live_plot for line in plot]

    def fps(self):
        self.counter += 1
        now = time.time()
        elapsed = now - self.timer
        if elapsed >= self.interval:
            if self.debug:
                print("FPS: %.2f" % (self.counter / elapsed))
            if (self.counter / elapsed) < 1.25 * self.interval:
                print("Warning: animation slowdown.")
            self.counter = 0
            self.timer = now
        return

    def animate(self):
        """
        Starts showing the plotting window. Blocks execution of subsequent code (except calls to self.update_plots())!
        :return: None
        """
        # instantiate animation
        self.ani = animation.FuncAnimation(fig=self.axes[0].figure, func=self.update_plots,
                                           interval=self.interval, blit=True, frames=itertools.count(start=1))
        plt.show(block=True)
        return

    def stop(self, _):
        if self.ani:
            if self.ani.event_source:
                self.ani.event_source.stop()
        matplotlib.use(self.original_backend)
        plt.close(self.fig)

    def exception_handler(self, exc, val, tb):
        """
        Used to stop the graphics backend from swallowing errors.
        """
        if exc == StopIteration:
            # This is an allowable error, it means the data generator function was exhausted
            # (or the parent wants us to stop).
            pass
        else:
            raise val
