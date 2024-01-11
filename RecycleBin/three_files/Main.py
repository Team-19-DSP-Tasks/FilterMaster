import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from scipy.signal import freqz, zpk2tf

import filterDesignBackend as back
from filterDesignUI import Ui_FilterDesigner


class MainWindow(QMainWindow, Ui_FilterDesigner):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # UI Objects Connections
        self.addPole.clicked.connect(lambda: back.pole_mode())
        self.addZero.clicked.connect(lambda: back.zero_mode())

        self.removeAllPoles.clicked.connect(
            lambda: back.remove_poles(self.unitCirclePlot)
        )
        self.removeAllZeros.clicked.connect(
            lambda: back.remove_zeros(self.unitCirclePlot)
        )
        self.resetDesign.clicked.connect(lambda: back.reset_design(self.unitCirclePlot))

        self.addConjugatesCheckBox.stateChanged.connect(
            lambda state: back.handle_conjugates(
                self.addConjugatesCheckBox, self.unitCirclePlot
            )
        )
        self.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: back.handle_unit_circle_click(
                event, self.unitCirclePlot, self.addConjugatesCheckBox
            )
        )

    def update_plots(self):
        self.plot_responses()

    def plot_responses(self):
        # Use Pyqtgraph to plot magnitude and phase responses
        zeros_array = np.array([complex(z.x(), z.y()) for z in back.zeros_positions])
        poles_array = np.array([complex(p.x(), p.y()) for p in back.poles_positions])

        numerator, denominator = zpk2tf(zeros_array, poles_array, 1)
        w, h = freqz(numerator, denominator)

        # Update magnitude response plot
        self.magFrequencyResponse.clear()
        self.magFrequencyResponse.setLogMode(x=True, y=True)
        self.magFrequencyResponse.plot(w, 20 * np.log10(abs(h)), pen="b")
        self.magFrequencyResponse.setLabel("left", "Magnitude (dB)")
        self.magFrequencyResponse.setLabel("bottom", "Frequency (rad/s)")
        self.magFrequencyResponse.showGrid(True, True)

        # Update phase response plot
        self.phaseFrequencyResponse.clear()
        self.phaseFrequencyResponse.setLogMode(x=True, y=False)
        self.phaseFrequencyResponse.plot(w, np.angle(h), pen="r")
        self.phaseFrequencyResponse.setLabel("left", "Phase (radians)")
        self.phaseFrequencyResponse.setLabel("bottom", "Frequency (rad/s)")
        self.phaseFrequencyResponse.showGrid(True, True)


if __name__ == "__main__":
    app = QApplication([])
    with open("UI_Layout/stylesheet.qss", "r") as f:
        stylesheet = f.read()
        app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.show()
    app.exec_()
