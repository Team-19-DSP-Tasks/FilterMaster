import numpy as np
from PyQt5 import QtCore
from pyqtgraph import PlotWidget


class MousePlotWidget(PlotWidget):
    dataPoint = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lastPos = None
        self.lastTime = None

    def mouseMoveEvent(self, event):
        self.dataPoint.emit(event.pos().y())
