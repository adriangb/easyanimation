from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import itertools
import numpy as np

class Thread(QtCore.QThread):
    dataChanged = QtCore.Signal(np.ndarray)

    def __init__(self, close_fun, data_function, plot_fun, interval, *args, **kwargs):
        super(Thread, self).__init__(*args, **kwargs)
        self.idx = 1
        self.data_function = data_function
        self.dataChanged.connect(plot_fun)
        self.interval = interval
        self.stop_parent = close_fun

    def run(self):
        self.threadactive = True
        while self.threadactive:
            try:
                data = self.data_function(self.idx)
                self.dataChanged.emit(data)
                self.idx += 1
                QtCore.QThread.msleep(self.interval)
            except StopIteration:
                self.stop()
                break

    def stop(self):
        self.threadactive = False
        self.stop_parent(None)
        self.wait()


class AnimatedFigure(object):
    def __init__(self, data_function, plot_samples, interval=1):
        # sys.stderr = object       # Can be used to disable unimportant errors / warnings
        self.app = QtGui.QApplication.instance()
        if self.app is None:
            self.app = QtGui.QApplication([])
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
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setBackground('w')
        self.axes = [None] * self.num_plots
        self.curves = [[None for _ in y[1:]] for y in init_data]

        # Workaround to be able to add labels before calling the animate() method
        for i in range(self.num_plots):
            self.axes[i] = self.win.addPlot()

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
        # Workaround to be able to add labels before calling the animate() method
        for i, plot in enumerate(self.curves):
            if len(plot) > 1:
                self.axes[i].addLegend()
            for j, curve in enumerate(plot):
                if self.curves[i][j] is None:
                    self.curves[i][j] = f"Curve {j}"
                self.curves[i][j] = self.axes[i].plot(pen=pg.mkPen(color=j, width=3), name=self.curves[i][j])
        self.thread = Thread(self.stop, self.data_function, self.update, self.interval)
        self.thread.start()
        self.app.exec_()

    def stop(self, _):
        self.app.closeAllWindows()



