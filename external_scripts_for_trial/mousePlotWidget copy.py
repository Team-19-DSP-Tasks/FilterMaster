import time

import numpy as np
from PyQt5 import QtCore
from pyqtgraph import PlotWidget


class CustomPlotWidget(PlotWidget):
    frequencySignal = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lastPos = None
        self.lastTime = None

    def mouseMoveEvent(self, event):
        if self.lastPos is None:
            self.lastPos = event.pos()
            self.lastTime = time.time()
        else:
            dx = event.pos().x() - self.lastPos.x()
            dy = event.pos().y() - self.lastPos.y()
            dt = time.time() - self.lastTime

            speed = np.sqrt(dx**2 + dy**2) / dt
            frequency = self.calculate_frequency(speed)

            self.frequencySignal.emit(frequency, event.pos().y())

            self.lastPos = event.pos()
            self.lastTime = time.time()

    def calculate_frequency(self, speed):
        # Define the speed range that corresponds to the frequency range
        speed_min = 0.0
        speed_max = 1000.0  # Adjust this value based on your specific use case

        # Define the frequency range
        frequency_min = 0.0
        frequency_max = 100.0  # Adjust this value based on your specific use case

        # Clamp the speed value to the defined range
        speed = np.clip(speed, speed_min, speed_max)

        # Map the speed value logarithmically to the frequency range
        speed_range = np.log(speed_max - speed_min)
        frequency_range = frequency_max - frequency_min
        frequency = frequency_min + frequency_range * (
            np.log(speed - speed_min) / speed_range
        )

        return frequency


"""
signal_value = np.sqrt(pos.x()**2 + pos.y()**2) * 10
self.data.append(signal_value)
"""
