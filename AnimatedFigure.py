# Set backend
import matplotlib

try:
    matplotlib.use('TkAgg')
    print("Switched graphics backend to Tkinter for compatibility.")
except:
    print("Unable to load TkAgg.")
    print("Please to go to Tools > Preferences > IPython Console > Graphics and change Backend to \"Tkinter\"")
    raise

# Imports
import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt

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
        self.timer = 0
        self.debug = debug
        # initialize figure
        self.interval = interval
        self.plot_samples = plot_samples
        self.data_function = data_function
        init_data = self.data_function(0)
        self.num_plots = len(init_data)
        # make copies to avoid overwriting mutable objects
        initial_plot_data = []
        for y_data in init_data:
            sublist = []
            for y in y_data[1:]:
                new_line = np.zeros(self.plot_samples)
                sublist.append(new_line)
            initial_plot_data.append(sublist)
        self.fig = plt.figure()
        self.axes = self.fig.subplots(1, self.num_plots, squeeze=False)[0]
        self.fig.canvas.mpl_connect('close_event', self.stop)
        try:
            self.fig.canvas._master.report_callback_exception = self.exception_handler
        except AttributeError:
            print("Could not connect plot close callback to KeyBoardInterrupt")
        self.live_plot = []
        for ax, y_data in zip(self.axes, initial_plot_data):
            sublist = []
            for y in y_data:
                new_line = ax.plot(y)[0]
                sublist.append(new_line)
            self.live_plot.append(sublist)
        plt.tight_layout()
        self.ani = None  # placeholder for animation object

    def update_plots(self, idx):
        """
        Updates the live-plots based on new data collected.
        A maximum of plot_samples data points will be plotted.
        Axis limits are automatically adjusted.
        :param idx: required parameter by FuncAnimation. It is not used.
        :return: list of objects (axis) updated.
        """
        def _update_x_labels():
            """
            Rescale/relabel x axis.
            Number and location of ticks is left to be auto determined, we just change the labels.
            :return: boolean indicating if redraw is necessary.
            """
            # If there are enough x-data points, update the x-axis labels
            if len(x) >= self.plot_samples:
                x_ticks = ax.get_xticks()
                x_tick_labels = [item.get_text() for item in ax.get_xticklabels() if len(item.get_text()) > 0]
                new_labels = [float(f'{x:1.1}') for x in x_ticks / self.plot_samples * (x[-1] - x[0])]
                if new_labels[0] != float(x_tick_labels[0].replace(u'\u2212', '-')) or new_labels[-1] != float(
                        x_tick_labels[-1].replace(u'\u2212', '-')):
                    ax.set_xticklabels(new_labels)
                    return True
            return False

        def _update_y_labels(y_data):
            """
            Rescale/relabel y axis. We don't use auto-scaling since that can cause hysteresis and unnecessary draws.
            :param y_data: aggregate of all y data on plat (i.e. join all y data)
            :return: boolean indicating if redraw is necessary.
            """
            # check if data is out of range of axis, if so force y-axis to update
            y_valid = [val for val in y_data if val is not None and not np.isnan(val)]
            if len(y_valid) >= 2:
                old_ymin, old_ymax = ax.get_ylim()
                data_range = np.nanmax(y_valid) - np.nanmin(y_valid)
                new_max_lim = np.nanmax(y_valid) + data_range * 0.1
                new_min_lim = np.nanmin(y_valid) - data_range * 0.1
                if new_max_lim == new_min_lim:
                    new_max_lim = np.nanmax(y_valid) + .1  # ensures if the line is constant axis are still scaled
                    new_min_lim = np.nanmin(y_valid) - .1  # ensures if the line is constant axis are still scaled
                if not ((.9 < old_ymax / new_max_lim < 1.1) and (.9 < old_ymin / new_min_lim < 1.1)):
                    new_labels = [float(f'{num:1.1}') for num in
                                  np.linspace(new_min_lim, new_max_lim, len(ax.get_yticks()))]
                    ax.set_ylim(bottom=new_min_lim, top=new_max_lim)
                    ax.set_yticks(new_labels)
                    return True
            return False

        self.fps()

        data = self.data_function(idx)  # data_function must return a tuple containing lists of x,y data

        for plot_num, (ax, (x, *y_points)) in enumerate(zip(self.axes, data)):

            # Slice the data to the right number of samples
            y_points = [y[-self.plot_samples:] for y in y_points]

            # Do the actual updating of the data, depending on blitting setting
            len_dif = self.plot_samples - len(y_points[0])
            if len_dif > 0:
                y_points = [np.append(np.repeat(np.nan, repeats=len_dif), y) for y in y_points]
                # This way we can accept any iterable as y
            for line, y in zip(self.live_plot[plot_num], y_points):
                line.set_ydata(y)

            if idx % (self.plot_samples / 2) == 0 and idx > 10:
                # Only check every couple frames for speed
                # Labels will not update properly on the first couple frames, skip them
                if _update_x_labels() or _update_y_labels(y_data=[y_point for y_list in y_points for y_point in y_list]):
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
        self.ani = animation.FuncAnimation(
            fig=self.axes[0].figure, func=self.update_plots, interval=self.interval, blit=True)
        plt.show(block=True)
        return

    def stop(self, _):
        self.ani.event_source.stop()
        try:
            import IPython
            shell = IPython.get_ipython()
            shell.enable_matplotlib(gui='inline')
        except (ModuleNotFoundError, ImportError):
            print("Unable to reset graphics backend")
            # This is not a deal breaker and would be normal if the class is used in a Python console
        raise KeyboardInterrupt

    def exception_handler(self, exc, val, tb):
        raise exc
