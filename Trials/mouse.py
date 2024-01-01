import sys
import time
from collections import deque

import matplotlib.pyplot as plt
import mouse
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from scipy.fftpack import fft


class MouseTracker(QMainWindow):
    def __init__(self):
        super(MouseTracker, self).__init__()

        self.setWindowTitle("Mouse Movement Tracker")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.mouse_positions = deque(maxlen=100)
        self.time_stamps = deque(maxlen=100)

        self.timer_interval = (
            0.05  # Set the interval for mouse movement recording in seconds
        )
        self.timer = self.startTimer(int(self.timer_interval * 1000))

    def timerEvent(self, event):
        x, y = mouse.get_position()
        self.mouse_positions.append((x, y))
        self.time_stamps.append(time.time())

        self.update_plot()

    def update_plot(self):
        self.ax1.clear()
        self.ax2.clear()

        positions = np.array(self.mouse_positions)
        time_diff = np.diff(np.array(self.time_stamps))
        frequency = 1.0 / time_diff

        self.ax1.plot(positions[:, 0], label="X Position")
        self.ax1.plot(positions[:, 1], label="Y Position")
        self.ax1.legend()

        self.ax2.plot(frequency, label="Frequency")
        self.ax2.legend()

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MouseTracker()
    window.show()
    sys.exit(app.exec_())
