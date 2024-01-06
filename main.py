import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

import filterDesignBackend as back
from filterDesignUI import Ui_FilterDesigner


class MainWindow(QMainWindow, Ui_FilterDesigner):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Predefined Data to real time plotting
        self.max_data_points = 4500  # trim data
        self.data = np.loadtxt("signals/leadII_ecg_fibrillation.csv", delimiter=",")
        self.data = self.data[-1 * self.max_data_points :]

        # UI Objects Connections
        self.addZero.clicked.connect(lambda: back.create_zero())
        self.addPole.clicked.connect(lambda: back.create_pole())
        self.removeAllPoles.clicked.connect(
            lambda: back.removePoles(self.unitCirclePlot)
        )
        self.removeAllZeros.clicked.connect(
            lambda: back.removeZeros(self.unitCirclePlot)
        )
        self.resetDesign.clicked.connect(lambda: back.reset(self.unitCirclePlot))
        self.addConjugatesCheckBox.stateChanged.connect(
            lambda state: back.addConjugates(
                self.addConjugatesCheckBox, self.unitCirclePlot
            )
        )

        # Connect the mouseClickEvent signal to the handleUnitCircleClick method
        self.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: back.handleUnitCircleClick(
                event, unitCirclePlot=self.unitCirclePlot
            )
        )
        self.actionImport_Signal.triggered.connect(
            lambda: back.importSignal(self.originalApplicationSignal)
        )

        # Predefined Real Time Plotting
        self.updateInterval = 50
        self.timer = QTimer(self)
        self.timer.timeout.connect(
            lambda: back.updatePlot(self.originalApplicationSignal, self.data)
        )
        self.timer.start(self.updateInterval)


if __name__ == "__main__":
    app = QApplication([])
    with open("UI_Layout/stylesheet.qss", "r") as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    app.exec_()
