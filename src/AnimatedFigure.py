# Set backend
import matplotlib

try:
    # Switch graphics backend to TkAgg to be able to function in IPython
    matplotlib.use('TkAgg')
except:
    print("Unable to load TkAgg.")
    print("If using Spyder: Please to go to Tools > Preferences > IPython Console > Graphics and change Backend to \"Tkinter\"")
    raise

# Imports
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
import itertools
import time


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
        :return: boolean indicating if redraw is necessary.
        """
        # If there are enough x-data points, update the x-axis labels
        if len(x) >= plot_samples:
            x_ticks = ax.get_xticks()
            x_tick_labels = [item.get_text() for item in ax.get_xticklabels() if len(item.get_text()) > 0]
            new_labels = [float(f'{x:1.1}') for x in x_ticks / plot_samples * (x[-1] - x[0])]
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
        # check if data is out of range of axis, if so force y-axis to update
        y_valid = np.array([val for val in [y_point for y_list in y_points for y_point in y_list]
                            if val is not None and not np.isnan(val)])
        if len(y_valid) >= 2:
            old_ymin, old_ymax = ax.get_ylim()
            data_min, data_max = np.min(y_valid), np.max(y_valid)
            data_range = data_max - data_min
            new_max_lim = data_max + data_range * 0.1
            new_min_lim = data_min - data_range * 0.1
            if new_max_lim == new_min_lim:
                new_max_lim = data_max + .1  # ensures if the line is constant axis are still scaled
                new_min_lim = data_min - .1  # ensures if the line is constant axis are still scaled
            if not ((.85 < old_ymax / new_max_lim < 1.15) and (.85 < old_ymin / new_min_lim < 1.15)):
                new_labels = [float(f'{num:1.1}') for num in
                              np.linspace(new_min_lim, new_max_lim, len(ax.get_yticks()))]
                ax.set_ylim(bottom=new_min_lim, top=new_max_lim)
                ax.set_yticks(new_labels)
                return True
        return False

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

            # Get length of data
            # Assumes all y data within a subplot is of the same length
            y_lengths = [len(y) for y in y_points]
            assert np.count_nonzero(np.diff(y_lengths)) == 0, "y data must all be of same length within a subplot."
            y_len = min(y_lengths[0], plot_samples)

            # Slice the data to the right number of samples
            y_points = [list(itertools.islice(y, max(len(y) - plot_samples, 0), None)) for y in y_points]
            x = list(itertools.islice(x, max(len(x) - plot_samples, 0), None))
            # Slice first, convert to list later.
            # This is faster and uses less memory if the iterable is a long non-slicable object (ex: deque)
            # A list is needed because we need to know the length.

            # Do the actual updating of the data, depending on blitting setting
            len_dif = plot_samples - y_len
            if len_dif > 0:
                y_points = [list(itertools.chain((np.nan for _ in range(len_dif)), y)) for y in y_points]
                # This way we can accept any iterable as y
            for line, y in zip(self.live_plot[plot_num], y_points):
                line.set_ydata(y)

            if idx % (plot_samples / 2) == 0 and idx > 10:
                # Only check every couple frames for speed
                # Labels will not update properly on the first couple frames, skip them
                if self._update_x_labels(ax, x, plot_samples) or self._update_y_labels(ax, y_points):
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
        try:
            import IPython
            shell = IPython.get_ipython()
            shell.enable_matplotlib(gui='inline')
            print("Unable to reset graphics backend")
        except (ModuleNotFoundError, ImportError):
            pass
            # In this case, this was probably not run in IPython
        finally:
            plt.close(self.fig)
        return

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
