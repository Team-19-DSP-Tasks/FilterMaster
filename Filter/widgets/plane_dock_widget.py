import csv

from PyQt5.QtCore import QPointF, pyqtSignal
from PyQt5.QtWidgets import QDockWidget


class PlaneDockWidget(QDockWidget):
    # Set a signal to be able to plot the filter once dropped
    csvDropped = pyqtSignal(list, list, list, list)

    def __init__(self, parent=None):
        super(PlaneDockWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.zero_tuples = []
        self.pole_tuples = []
        self.allpass_zero_tuples = []
        self.allpass_pole_tuples = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".csv"):
                self.load_csv(path)

    def load_csv(self, path):
        with open(path, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if len(row) != 0:
                    x = float(row[1])
                    y = float(row[2])
                    if row[0] == "zero":
                        self.zero_tuples.append(QPointF(x, y))
                    elif row[0] == "pole":
                        self.pole_tuples.append(QPointF(x, y))
                    elif row[0] == "allpass zero":
                        self.allpass_zero_tuples.append(QPointF(x, y))
                    elif row[0] == "allpass pole":
                        self.allpass_pole_tuples.append(QPointF(x, y))
            self.csvDropped.emit(
                self.zero_tuples,
                self.pole_tuples,
                self.allpass_zero_tuples,
                self.allpass_pole_tuples,
            )
