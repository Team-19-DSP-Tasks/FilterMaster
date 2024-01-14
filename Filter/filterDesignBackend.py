import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
import wfdb
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from pyqtgraph import TargetItem
from scipy.signal import freqz, zpk2tf


class CustomTargetItem(pg.TargetItem):
    def __init__(
        self,
        plot,
        *args,
        **kwargs,
    ):
        # poles,
        # poles_positions,
        # poles_conjugates,
        # poles_conjugates_positions,
        super().__init__(*args, **kwargs)
        self.plot = plot
        # self.poles = poles
        # self.poles_positions = poles_positions
        # self.poles_conjugates = poles_conjugates
        # self.poles_conjugates_positions = poles_conjugates_positions

    def mouseClickEvent(self, event):
        if event.button() == pg.QtCore.Qt.RightButton:
            self.contextMenuEvent(event)

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        removeAction = QAction("Remove", None)
        removeAction.triggered.connect(self.remove)
        contextMenu.addAction(removeAction)
        contextMenu.exec_(event.screenPos())

    def remove(self):
        self.plot.removeItem(self)
        # self.poles.remove(self)
        # self.poles_positions.remove(self.pos())
        # self.poles_conjugates.remove(self)
        # self.poles_conjugates_positions.remove(self.pos())


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
        self.ui.actionImport_Signal.triggered.connect(self.import_signal)

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
        # Global Variables for real time plotting
        self.update_interval = 50
        self.originial_signal_timer = QTimer()
        self.originial_signal_timer.timeout.connect(self.update_plot)
        self.originial_signal_timer.start(self.update_interval)
        self.signal_index = 0
        self.predefined_data = np.loadtxt(
            "signals/leadII_ecg_fibrillation.csv", delimiter=","
        )

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
        conjugates_list.append(pg.Point(pos.x(), -pos.y()))
        index = positions_list.index(pos)
        # Connect the sigPositionChanged signal to the update_positions function
        item.sigPositionChanged.connect(lambda: self.update_positions(item, index))
        # Only call plot_responses once after all initial items are drawn
        self.update_responses()

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
        if self.ui.addConjugatesCheckBox.isChecked():
            if self.is_pole:
                self.draw_conjugates([self.poles_conjugates_positions[-1]], "x", "b")
            elif self.is_zero:
                self.draw_conjugates([self.zeros_conjugates_positions[-1]], "o", "y")

    def update_positions(self, item, index):
        new_pos = item.pos()
        if item in self.poles:
            self.poles_positions[index] = new_pos
            self.poles_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())
            if bool(self.poles_conjugates):
                self.poles_conjugates[index].setPos(
                    self.poles_conjugates_positions[index]
                )
        elif item in self.zeros:
            self.zeros_positions[index] = new_pos
            self.zeros_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())
            if bool(self.zeros_conjugates):
                self.zeros_conjugates[index].setPos(
                    self.zeros_conjugates_positions[index]
                )
        self.update_responses()

    # REMOVE All Zeros/Poles and RESET Design
    def remove_poles(self):
        self.remove(self.poles + self.poles_conjugates)
        # Empty all pole related lists
        self.poles.clear()
        self.poles_positions.clear()
        self.poles_conjugates.clear()
        self.poles_conjugates_positions.clear()
        self.update_responses()

    def remove_zeros(self):
        self.remove(self.zeros + self.zeros_conjugates)
        # Empty all zero related lists
        self.zeros.clear()
        self.zeros_positions.clear()
        self.zeros_conjugates.clear()
        self.zeros_conjugates_positions.clear()
        self.update_responses()

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
        self.update_responses()

    def remove(self, whichList):
        for item in whichList:
            self.ui.unitCirclePlot.removeItem(item)
        self.update_responses()

    # HANDLING CONJUGATES
    def draw_conjugates(self, conjugates_positions, symbol, color):
        for pos in conjugates_positions:
            item = TargetItem(
                size=10,
                movable=False,
                symbol=symbol,
                pen=pg.mkPen(color),
            )
            item.setPos(pos)
            self.ui.unitCirclePlot.addItem(item)
            if symbol == "x":
                self.poles_conjugates.append(item)
            elif symbol == "o":
                self.zeros_conjugates.append(item)

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

    # APPLICATION SIGNALS PLOTTING
    def import_signal(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Open Signal Files",
            "",
            "Signal Files (*.csv *.hea *.dat);;All Files (*)",
            options=options,
        )

        if file_path:
            try:
                if file_path.endswith(".hea") or file_path.endswith(".dat"):
                    # Read signal data from .hea and .dat files using wfdb library
                    record = wfdb.rdrecord(file_path[:-4])  # Remove ".hea" extension
                    self.predefined_data = record.p_signal[
                        :, 0
                    ]  # Use the first channel

                elif file_path.endswith(".csv"):
                    # Use pandas to read the CSV file
                    data_frame = pd.read_csv(file_path)
                    # Use the first column as the signal data
                    self.predefined_data = data_frame.iloc[:, 0].to_numpy()
                else:
                    pass

                self.signal_index = (
                    0  # Reset the signal index when a new signal is imported
                )
                self.update_plot()  # Use the new signal data for real-time plotting
                self.originial_signal_timer.start(self.update_interval)
            except Exception as e:
                print(f"Error loading the file: {e}")

    def update_plot(self):
        self.ui.originalApplicationSignal.clear()
        self.signal_index += 1
        if self.signal_index >= len(self.predefined_data):
            self.signal_index = 0
        x_data = np.arange(self.signal_index)
        y_data = self.predefined_data[: self.signal_index]
        y_max = max(y_data)
        y_min = min(y_data)
        self.ui.originalApplicationSignal.plot(x=x_data, y=y_data, pen="orange")
        self.ui.originalApplicationSignal.setYRange(y_min, y_max, padding=0.1)
        # Calculate the visible range for the X-axis based on the current signal_index
        visible_range = (self.signal_index - 150, self.signal_index)
        # Set the X-axis limits to control the visible range
        x_min_limit = 0
        x_max_limit = self.signal_index + 0.1
        self.ui.originalApplicationSignal.setLimits(
            xMin=x_min_limit, xMax=x_max_limit, yMin=y_min, yMax=y_max
        )
        self.ui.originalApplicationSignal.setXRange(*visible_range, padding=0)
