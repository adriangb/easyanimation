from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import itertools
import numpy as np
import sys


class Thread(QtCore.QThread):
    dataChanged = QtCore.Signal(np.ndarray)

    def __init__(self, data_function, plot_fun, interval, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.idx = 1
        self.data_function = data_function
        self.dataChanged.connect(plot_fun)
        self.interval = interval

    def run(self):
        while True:
            data= self.data_function(self.idx)
            self.dataChanged.emit(data)
            self.idx += 1
            QtCore.QThread.msleep(self.interval)


class AnimatedFigure(QtGui.QApplication):
    def __init__(self, data_function, plot_samples, interval=1):
        super(AnimatedFigure, self).__init__([])
        sys.stderr = object

        # get data updating function & initialize plot params
        self.interval = interval
        self.data_function = data_function
        init_data = self.data_function(0)
        self.num_plots = len(init_data)
        try:
            if len(plot_samples) > 1:
                assert self.num_plots == len(plot_samples), \
                    f"Size of plot_samples is {len(plot_samples)} while data_function signature is {self.num_plots}."
                self.plot_samples = plot_samples
        except TypeError:
            self.plot_samples = [plot_samples for _ in range(self.num_plots)]

        # initialize plots
        self.win = pg.GraphicsWindow()
        self.plots = [None]*self.num_plots
        self.curves = [[None for _ in y[1:]] for y in init_data]
        for i, (xy_data, plot_samples) in enumerate(zip(init_data, self.plot_samples)):
            self.plots[i] = self.win.addPlot()
            for j, y_data in enumerate(xy_data[1:]):
                self.curves[i][j] = self.plots[i].plot()
        self.thread = Thread(self.data_function, self.update, self.interval)

    @QtCore.Slot(np.ndarray)
    def update(self, data):
        for i, (plot_data, plot_samples) in enumerate(zip(data, self.plot_samples)):
            for j, y_data in enumerate(plot_data[1:]):
                y = list(itertools.islice(y_data, max(len(y_data) - plot_samples, plot_samples)))
                self.curves[i][j].setData(y)

    def animate(self):
        self.thread.start()
        self.exec_()
