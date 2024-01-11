import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from scipy.signal import freqz, zpk2tf


def plot_responses():
    global zeros_positions, poles_positions

    zeros_array = np.array([complex(z.x(), z.y()) for z in zeros_positions])
    poles_array = np.array([complex(p.x(), p.y()) for p in poles_positions])

    numerator, denominator = zpk2tf(zeros_array, poles_array, 1)
    w, h = freqz(numerator, denominator)

    # Create a Pyqtgraph window
    app = QtGui.QGuiApplication([])
    win = pg.GraphicsView(title="Filter Response")
    win.resize(1000, 600)

    # Create two plot items for magnitude and phase
    plot1 = win.addPlot(title="Magnitude Response")
    plot2 = win.addPlot(title="Phase Response")

    # Plot magnitude response
    plot1.setLogMode(x=True, y=True)
    plot1.plot(w, 20 * np.log10(abs(h)), pen="b")
    plot1.setLabel("left", "Magnitude (dB)")
    plot1.setLabel("bottom", "Frequency (rad/s)")
    plot1.showGrid(True, True)

    # Plot phase response
    plot2.setLogMode(x=True, y=False)
    plot2.plot(w, np.angle(h), pen="r")
    plot2.setLabel("left", "Phase (radians)")
    plot2.setLabel("bottom", "Frequency (rad/s)")
    plot2.showGrid(True, True)

    # Start the PyQtGraph event loop
    QtGui.QApplication.instance().exec_()


# Example usage
# Assuming you have some data in zeros_positions and poles_positions
zeros_positions = [pg.Point(0.1, 0.2), pg.Point(0.2, 0.3)]
poles_positions = [pg.Point(0.05, 0.1), pg.Point(0.15, 0.25)]

plot_responses()
