import csv
import sys

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget


class RealTimePlotWidget(QWidget):
    def __init__(self, filename, update_interval=100):
        super(RealTimePlotWidget, self).__init__()

        self.filename = filename
        self.update_interval = update_interval

        self.plot_widget = pg.PlotWidget()
        self.plot_data_item = self.plot_widget.plot()

        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)

        self.setLayout(layout)

        self.data = np.array([])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(self.update_interval)

    def update_plot(self):
        new_data = self.read_csv_data()
        self.data = np.append(self.data, new_data)

        # Trim data to a fixed length for better performance
        max_data_points = 1000
        if len(self.data) > max_data_points:
            self.data = self.data[-max_data_points:]

        self.plot_data_item.setData(self.data)

    def read_csv_data(self):
        # Read data from the CSV file
        try:
            with open(self.filename, "r") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header if present
                data = np.array([float(row[0]) for row in reader])
                return data
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return np.array([])


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = RealTimePlotWidget(filename="your_file.csv")
        self.setCentralWidget(self.central_widget)

        self.setWindowTitle("Real-Time Plotting Example")
        self.setGeometry(100, 100, 800, 600)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
