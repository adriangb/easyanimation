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
        # sys.stderr = object       # Can be used to disable unimportant errors / warnings

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
        pg.setConfigOption('background', 'w')
        self.win = pg.GraphicsWindow()
        self.axes = [None] * self.num_plots
        self.curves = [[None for _ in y[1:]] for y in init_data]
        for i, (xy_data, plot_samples) in enumerate(zip(init_data, self.plot_samples)):
            self.axes[i] = self.win.addPlot()
            for j, y_data in enumerate(xy_data[1:]):
                self.curves[i][j] = self.axes[i].plot(pen=pg.mkPen(color=j, width=3))
        self.thread = Thread(self.data_function, self.update, self.interval)

    @QtCore.Slot(np.ndarray)
    def update(self, data):
        for i, (plot_data, plot_samples) in enumerate(zip(data, self.plot_samples)):
            for j, y_data in enumerate(plot_data[1:]):
                x = list(itertools.islice(plot_data[0], max(len(plot_data[0]) - plot_samples, 0), None))
                # Note that computing x 1 time would be more efficient, but because of timing issues this can lead
                # to a mismatch between len(x) and len(y)
                y = list(itertools.islice(y_data, max(len(y_data) - plot_samples, 0), None))
                if len(x) != len(y):
                    # Debug code to catch length difference issues, may be system dependant
                    print(f"lens of orig: {len(plot_data[0])}, {len(y_data)}")
                    print(f"lens of sliced: {len(x)}, {len(y)}")
                    print(f"lens of slice start: "
                          f"{max(len(plot_data[0]) - plot_samples, 0)}, {max(len(y_data) - plot_samples, 0)}")
                self.curves[i][j].setData(x=x, y=y)

    def animate(self):
        self.thread.start()
        self.exec_()
