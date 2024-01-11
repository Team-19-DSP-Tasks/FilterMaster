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

        self.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: back.handleUnitCircleClick(
                event, self.unitCirclePlot, self.addConjugatesCheckBox
            )
        )


if __name__ == "__main__":
    app = QApplication([])
    with open("UI_Layout/stylesheet.qss", "r") as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    app.exec_()
