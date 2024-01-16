# import csv
# import sys

# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from PyQt5.QtCore import Qt
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


# class MainWindow(QMainWindow):
#     def __init__(self):
#         super(MainWindow, self).__init__()

#         self.setWindowTitle("Mouse Coordinate Logger")
#         self.setGeometry(100, 100, 800, 600)

#         self.central_widget = QWidget(self)
#         self.setCentralWidget(self.central_widget)

#         self.setup_ui()

#     def setup_ui(self):
#         self.layout = QVBoxLayout(self.central_widget)

#         # Create Matplotlib Figure and Canvas
#         self.figure, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.figure)
#         self.layout.addWidget(self.canvas)

#         # Create QPushButton
#         self.button = QPushButton("Start Logging", self)
#         self.layout.addWidget(self.button)

#         # Connect button click signal to the start_logging function
#         self.button.clicked.connect(self.start_logging)

#         # Initialize logging status
#         self.is_logging = False

#         # Initialize CSV file and writer
#         self.csv_file = open("mouse_coordinates_log.csv", "w", newline="")
#         self.csv_writer = csv.writer(self.csv_file)
#         self.csv_writer.writerow(["X", "Y"])

#         # Connect the mouse move event to the on_mouse_move function
#         self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

#     def start_logging(self):
#         if not self.is_logging:
#             self.is_logging = True
#             self.button.setText("Stop Logging")
#         else:
#             self.is_logging = False
#             self.button.setText("Start Logging")

#     def on_mouse_move(self, event):
#         if self.is_logging:
#             if event.xdata is not None and event.ydata is not None:
#                 x = event.xdata
#                 y = event.ydata
#                 if 0 <= x <= 100 and -50 <= y <= 50:
#                     # Log mouse coordinates to the CSV file
#                     self.csv_writer.writerow([f"{x:.2f}", f"{y:.2f}"])
#                     self.csv_file.flush()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQtGraph PlotWidget")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a vertical layout for the central widget
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create a PlotWidget and add it to the layout
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

        # Create a checkable button and add it to the layout
        self.generate_button = QPushButton("Generate")
        self.generate_button.setCheckable(True)
        layout.addWidget(self.generate_button)

        # Connect the button to a function that starts/stops recording mouse movement
        self.generate_button.clicked.connect(self.on_generate_button_clicked)

        # Initialize x and y lists
        self.x_data = []
        self.y_data = []

    def on_generate_button_clicked(self):
        if self.generate_button.isChecked():
            # Start recording mouse movement
            self.plot_widget.scene().sigMouseMoved.connect(self.on_mouse_moved)
        else:
            # Stop recording mouse movement
            self.plot_widget.scene().sigMouseMoved.disconnect(self.on_mouse_moved)

    def on_mouse_moved(self, evt):
        # Get the x and y data of the mouse movement and store them in two lists
        pos = evt  # evt is a QPointF object
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            self.x_data.append(mouse_point.x())
            self.y_data.append(mouse_point.y())

            print(f"x: {mouse_point.x()}, y: {mouse_point.y()}")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
