import sys

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class DraggableSymbol:
    def __init__(self, ax, symbol, x, y):
        self.ax = ax
        self.symbol = symbol
        self.circle = Circle((x, y), radius=0.1, color="red", fill=False, picker=True)
        self.ax.add_patch(self.circle)
        self.x = x
        self.y = y
        self.press = None

    def connect(self):
        self.cidpress = self.circle.figure.canvas.mpl_connect(
            "pick_event", self.on_press
        )
        self.cidrelease = self.circle.figure.canvas.mpl_connect(
            "button_release_event", self.on_release
        )
        self.cidmotion = self.circle.figure.canvas.mpl_connect(
            "motion_notify_event", self.on_motion
        )

    def on_press(self, event):
        if event.artist == self.circle:
            self.press = (
                self.circle.center[0] - event.xdata,
                self.circle.center[1] - event.ydata,
            )

    def on_motion(self, event):
        if self.press is None or event.inaxes != self.ax:
            return
        dx, dy = self.press
        self.x = event.xdata + dx
        self.y = event.ydata + dy
        self.circle.set_center((self.x, self.y))
        self.circle.figure.canvas.draw()

    def on_release(self, event):
        self.press = None
        self.circle.figure.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal", adjustable="datalim")
        self.ax.add_patch(Circle((0, 0), radius=1, color="black", fill=False))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.zero_button = QPushButton("Add Zero", self)
        self.zero_button.clicked.connect(self.add_zero)
        self.pole_button = QPushButton("Add Pole", self)
        self.pole_button.clicked.connect(self.add_pole)

        self.layout.addWidget(self.zero_button)
        self.layout.addWidget(self.pole_button)

        self.symbols = []

    def add_zero(self):
        zero = DraggableSymbol(self.ax, "o", 0, 0)
        zero.connect()
        self.symbols.append(zero)

    def add_pole(self):
        pole = DraggableSymbol(self.ax, "x", 0, 0)
        pole.connect()
        self.symbols.append(pole)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
