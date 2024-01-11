import logging

import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from pyqtgraph import TargetItem
from scipy.signal import freqz, zpk2tf

logging.basicConfig(
    level=logging.DEBUG,
    filename="log.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add an empty line to the log file
with open("log.log", "a") as log_file:
    log_file.write("\n")


class Backend:
    def __init__(self, ui):
        self.ui = ui

        # UI Objects Connections
        self.ui.addPole.clicked.connect(lambda: self.pole_mode())
        self.ui.addZero.clicked.connect(lambda: self.zero_mode())

        self.ui.removeAllPoles.clicked.connect(lambda: self.remove_poles())
        self.ui.removeAllZeros.clicked.connect(lambda: self.remove_zeros())
        self.ui.resetDesign.clicked.connect(lambda: self.reset_design())

        self.ui.addConjugatesCheckBox.stateChanged.connect(
            lambda state: self.handle_conjugates()
        )
        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: self.handle_unit_circle_click(event)
        )

        # To control poles and zeros creation
        self.is_pole = False
        self.is_zero = False
        # To store poles and zeros TargetItems
        self.poles = []
        self.zeros = []
        self.poles_conjugates = []
        self.zeros_conjugates = []
        # To store positions of poles and zeros
        self.poles_positions = []
        self.zeros_positions = []
        self.poles_conjugates_positions = []
        self.zeros_conjugates_positions = []
        # For plotting magnitude and phase responses
        self.mag_curve = pg.PlotCurveItem(pen="b")
        self.phase_curve = pg.PlotCurveItem(pen="r")
        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.magFrequencyResponse.addItem(self.mag_curve)
        self.ui.phaseFrequencyResponse.addItem(self.phase_curve)

    # CREATING Zeros and Poles
    def pole_mode(self):
        self.is_pole = True
        self.is_zero = False

    def zero_mode(self):
        self.is_pole = False
        self.is_zero = True

    def draw_item(self, pos, symbol, color, items, positions_list, conjugates_list):
        item = TargetItem(
            pos=pos,
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        self.ui.unitCirclePlot.addItem(item)
        items.append(item)
        positions_list.append(pos)
        conjugates_list.append(
            pg.Point(pos.x(), -pos.y())
        )  # Add the conjugate position
        if self.is_pole:
            self.poles_conjugates_positions.append(pg.Point(pos.x(), -pos.y()))
        elif self.is_zero:
            self.zeros_conjugates_positions.append(pg.Point(pos.x(), -pos.y()))
        index = positions_list.index(pos)
        # Connect the sigPositionChanged signal to the update_positions function
        item.sigPositionChanged.connect(lambda: self.update_positions(item, index))
        # Only call plot_responses once after all initial items are drawn
        # self.plot_responses()

    def handle_unit_circle_click(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pos = self.ui.unitCirclePlot.mapToView(event.scenePos())
            if self.is_pole:
                self.draw_item(
                    pos,
                    "x",
                    "r",
                    self.poles,
                    self.poles_positions,
                    self.poles_conjugates_positions,
                )
            elif self.is_zero:
                self.draw_item(
                    pos,
                    "o",
                    "g",
                    self.zeros,
                    self.zeros_positions,
                    self.zeros_conjugates_positions,
                )

    def update_positions(self, item, index):
        # Update the position in the list when the item is moved
        new_pos = item.pos()
        if item in self.poles:
            self.poles_positions[index] = new_pos
            self.poles_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())
        elif item in self.zeros:
            self.zeros_positions[index] = new_pos
            self.zeros_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())
        self.update_responses()

    # REMOVE All Zeros/Poles and RESET Design
    def remove_poles(self):
        self.remove(self.poles + self.poles_conjugates)
        # Empty all pole related lists
        self.poles.clear()
        self.poles_positions.clear()
        self.poles_conjugates.clear()
        self.poles_conjugates_positions.clear()

    def remove_zeros(self):
        self.remove(self.zeros + self.zeros_conjugates)
        # Empty all zero related lists
        self.zeros.clear()
        self.zeros_positions.clear()
        self.zeros_conjugates.clear()
        self.zeros_conjugates_positions.clear()

    def reset_design(self):
        self.remove(
            self.poles + self.poles_conjugates + self.zeros + self.zeros_conjugates,
        )
        # Empty all lists
        self.poles.clear()
        self.poles_positions.clear()
        self.poles_conjugates.clear()
        self.poles_conjugates_positions.clear()
        self.zeros.clear()
        self.zeros_positions.clear()
        self.zeros_conjugates.clear()
        self.zeros_conjugates_positions.clear()

    def remove(self, whichList):
        for item in whichList:
            self.ui.unitCirclePlot.removeItem(item)
        self.update_responses()

    # HANDLING CONJUGATES
    def draw_conjugates(self, conjugates_positions, symbol, color):
        for pos in conjugates_positions:
            item = TargetItem(
                size=10,
                movable=True,
                symbol=symbol,
                pen=pg.mkPen(color),
            )
            item.setPos(pos)
            self.ui.unitCirclePlot.addItem(item)
            if symbol == "x":
                self.poles_conjugates.append(item)
            elif symbol == "o":
                self.zeros_conjugates.append(item)
        self.update_responses()

    def handle_conjugates(self):
        if self.ui.addConjugatesCheckBox.isChecked():
            self.draw_conjugates(self.poles_conjugates_positions, "x", "b")
            self.draw_conjugates(self.zeros_conjugates_positions, "o", "y")
        else:
            self.remove(self.poles_conjugates + self.zeros_conjugates)
            self.poles_conjugates.clear()
            self.zeros_conjugates.clear()

    # PLOT MAGNITUDE AND PHASE RESPONSES
    def update_responses(self):
        # Get poles and zeros positions
        zeros_array = np.array([complex(z.x(), z.y()) for z in self.zeros_positions])
        poles_array = np.array([complex(p.x(), p.y()) for p in self.poles_positions])

        # Calculate magnitude and phase responses
        numerator, denominator = zpk2tf(zeros_array, poles_array, 1)
        w, h = freqz(numerator, denominator)

        # Update magnitude response plot
        self.mag_curve.setData(w, 20 * np.log10(abs(h)))

        # Update phase response plot
        self.phase_curve.setData(w, np.angle(h))

    def plot_responses(self):
        zeros_array = np.array([complex(z.x(), z.y()) for z in self.zeros_positions])
        poles_array = np.array([complex(p.x(), p.y()) for p in self.poles_positions])

        numerator, denominator = zpk2tf(zeros_array, poles_array, 1)
        w, h = freqz(numerator, denominator)

        # Update magnitude response plot
        self.ui.magFrequencyResponse.clear()
        self.mag_curve.setData(w, 20 * np.log10(abs(h)))

        # Update phase response plot
        self.ui.phaseFrequencyResponse.clear()
        self.phase_curve.setData(w, np.angle(h))
        self.update_responses()
