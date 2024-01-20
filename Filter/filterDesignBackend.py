import csv
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyqtgraph as pg
import wfdb
from Classes.libraryButton import ProcessButton
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu
from pyqtgraph import TargetItem
from scipy import signal
from scipy.signal import freqz, zpk2tf

# A folder to store the phase response plots of all-pass filters
save_directory = "Resources/All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)


class Backend:
    def __init__(self, ui):
        self.ui = ui

        # UI Objects Connections
        self.ui.addPole.clicked.connect(lambda: self.pole_mode())
        self.ui.addZero.clicked.connect(lambda: self.zero_mode())

        self.ui.removeAllPoles.clicked.connect(lambda: self.remove_poles())
        self.ui.removeAllZeros.clicked.connect(lambda: self.remove_zeros())
        self.ui.resetDesign.clicked.connect(lambda: self.reset_design())

        self.ui.actionImport_Signal.triggered.connect(self.import_signal)
        self.ui.exportSignal.clicked.connect(lambda: self.export())
        self.ui.exportFilter.clicked.connect(lambda: self.export_filter())
        self.ui.filtration_slider.valueChanged.connect(
            lambda: self.update_filtration_rate()
        )
        self.ui.applyFilterButton.clicked.connect(lambda: self.apply_filter())
        self.ui.correctPhase.clicked.connect(
            lambda: self.plot_all_pass_zeros_and_poles()
        )
        self.ui.addAllPassFilter.clicked.connect(lambda: self.add_all_pass_filter())
        self.ui.allPassEnteredValue.editingFinished.connect(
            lambda: self.add_all_pass_filter()
        )
        self.ui.pause_play_button.toggled.connect(
            lambda checked: self.pause_play_action(checked)
        )
        self.ui.addConjugatesCheckBox.stateChanged.connect(
            lambda: self.handle_conjugates()
        )
        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: self.handle_unit_circle_click(event)
        )
        self.ui.generateSignal.toggled.connect(
            lambda checked: self.start_generating(checked)
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
        # For Z-Plane Filter Calculations
        self.zeros_array = None
        self.poles_array = None
        self.numerator = None
        self.denominator = None
        # For All-Pass zeros and poles plotting
        self.all_pass_zeros = []
        self.all_pass_poles = []
        self.all_pass_zeros_positions = []
        self.all_pass_poles_positions = []
        # For plotting magnitude and phase responses of Z-Plane Filter
        self.mag_curve = pg.PlotCurveItem(pen="b")
        self.phase_curve = pg.PlotCurveItem(pen="r")
        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.magFrequencyResponse.addItem(self.mag_curve)
        self.ui.phaseFrequencyResponse.addItem(self.phase_curve)
        # Variables for real time plotting
        self.update_interval = 50
        self.plotting_timer = QTimer()
        self.plotting_timer.timeout.connect(self.update_real_time_plots)
        self.plotting_timer.start(self.update_interval)
        self.signal_index = 0
        # Data storing variables to be plotted: initially defined
        self.original_data = np.loadtxt(
            "Resources/signals/leadII_ecg_fibrillation.csv", delimiter=","
        )
        self.filtered_data = self.original_data
        # For Mouse Signal Generation
        self.mouse_signal_frequencies = []
        # All-Pass Library
        self.user_inputs_values = []
        self.idx = 10  # to accurately name the plot response of all-pass filter
        self.cascaded_filters = []  # includes the chosen filters to be cascaded
        self.all_pass_filters = [
            self.ui.allPass00,
            self.ui.allPass01,
            self.ui.allPass02,
            self.ui.allPass03,
            self.ui.allPass04,
            self.ui.allPass05,
            self.ui.allPass06,
            self.ui.allPass07,
            self.ui.allPass08,
        ]  # These are the predefined all-pass filters in the application

        for filter in self.all_pass_filters:
            filter.toggled.connect(
                lambda checked, button=filter: self.on_filter_chosen(checked, button)
            )

        # Set the initial state for the library appearance
        self.organize_library(self.ui.gridLayout, self.all_pass_filters)

    # =============================================================================================== #
    # =========================================== Methods =========================================== #
    # =============================================================================================== #

    # CREATING ZEROS AND POLES
    def pole_mode(self):
        self.is_pole = True
        self.is_zero = False

    def zero_mode(self):
        self.is_pole = False
        self.is_zero = True

    def handle_unit_circle_click(self, event):
        pos = self.ui.unitCirclePlot.mapToView(event.scenePos())
        if event.button() == QtCore.Qt.LeftButton:
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
                    self.draw_conjugates(
                        [self.poles_conjugates_positions[-1]], "x", "b"
                    )
                elif self.is_zero:
                    self.draw_conjugates(
                        [self.zeros_conjugates_positions[-1]], "o", "y"
                    )

        elif event.button() == QtCore.Qt.RightButton:
            self.create_context_menu(pos)

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
        # Update the magnitude and phase plotting if items are being moved
        self.update_responses()

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

    # REMOVE A SPECIFIC ZERO OR POLE
    def create_context_menu(self, clicked_position):
        # Context Menu to delete a specific zero or pole
        self.context_menu = QMenu()
        self.remove_action = QAction("Remove")
        # Connect the signal before executing the context menu
        self.remove_action.triggered.connect(lambda: self.remove_item(clicked_position))
        self.context_menu.addAction(self.remove_action)
        self.context_menu.exec_(QtGui.QCursor.pos())

    def remove_item(self, clicked_position):
        tolerance = 0.1
        for pole_pos in self.poles_positions:
            if (pole_pos - clicked_position).manhattanLength() < tolerance:
                index = self.poles_positions.index(pole_pos)
                item = self.poles[index]
                self.ui.unitCirclePlot.removeItem(item)
                self.poles.remove(item)
                self.poles_positions.remove(pole_pos)
                self.poles_conjugates_positions.remove(
                    self.poles_conjugates_positions[index]
                )
                if self.ui.addConjugatesCheckBox.isChecked():
                    self.ui.unitCirclePlot.removeItem(self.poles_conjugates[index])
                    self.poles_conjugates.remove(self.poles_conjugates[index])

        for zero_pos in self.zeros_positions:
            if (zero_pos - clicked_position).manhattanLength() < tolerance:
                index = self.zeros_positions.index(zero_pos)
                item = self.zeros[index]
                self.ui.unitCirclePlot.removeItem(item)
                self.zeros.remove(item)
                self.zeros_positions.remove(zero_pos)
                self.zeros_conjugates_positions.remove(
                    self.zeros_conjugates_positions[index]
                )
                if self.ui.addConjugatesCheckBox.isChecked():
                    self.ui.unitCirclePlot.removeItem(self.zeros_conjugates[index])
                    self.zeros_conjugates.remove(self.zeros_conjugates[index])

        self.update_responses()

    # REMOVE All ZEROS/POLES AND RESET DESIGN
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
        self.zeros_array = np.array(
            [complex(z.x(), z.y()) for z in self.zeros_positions]
        )
        self.poles_array = np.array(
            [complex(p.x(), p.y()) for p in self.poles_positions]
        )

        # Calculate magnitude and phase responses
        self.numerator, self.denominator = zpk2tf(self.zeros_array, self.poles_array, 1)
        frequencies_values, response_complex = freqz(self.numerator, self.denominator)

        # Update magnitude response plot
        self.mag_curve.setData(frequencies_values, 20 * np.log10(abs(response_complex)))

        # Update phase response plot
        self.phase_curve.setData(frequencies_values, np.angle(response_complex))

    # EXPORT THE DESIGNED FILTER
    def export_filter(self):
        if len(self.poles) == 0 and len(self.zeros) == 0:
            self.show_error(self.ui.emptyDesign, "Design is empty!")
        else:
            self.hide_error(self.ui.emptyDesign)
            fileName, _ = QFileDialog.getSaveFileName(
                None, "Save File", "", "CSV Files (*.csv)"
            )
            if fileName:
                with open(fileName, "w", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([None, "x", "y"])  # Write the column titles
                    for zero in self.zeros_positions:
                        writer.writerow(["zero", zero.x(), zero.y()])
                    writer.writerow([])
                    for pole in self.poles_positions:
                        writer.writerow(["pole", pole.x(), pole.y()])

    def export(self):
        fileName, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "CSV Files (*.csv)"
        )
        if fileName:
            np.savetxt(fileName, self.filtered_data, delimiter=",")

    def show_error(self, error_label, message):
        error_label.setText(f'<font color="#ef0f2e">{message}</font>')
        error_label.setVisible(True)

    def hide_error(self, error_label):
        error_label.clear()
        error_label.setVisible(False)

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
                    self.original_data = record.p_signal[:, 0]  # Use the first channel
                    self.filtered_data = self.original_data

                elif file_path.endswith(".csv"):
                    # Use pandas to read the CSV file
                    data_frame = pd.read_csv(file_path)
                    # Use the first column as the signal data
                    self.original_data = data_frame.iloc[:, 0].to_numpy()
                    self.filtered_data = self.original_data
                else:
                    pass

                # Reset the signal index when a new signal is imported
                self.signal_index = 0
                self.update_plot()  # Use the new signal data for real-time plotting
                self.plotting_timer.start(self.update_interval)
            except Exception as e:
                print(f"Error loading the file: {e}")

    def update_real_time_plots(self):
        self.update_plot(self.ui.originalApplicationSignal, self.original_data)
        self.update_plot(self.ui.filteredSignal, self.filtered_data)

    def update_plot(self, plot_widget, signal_data):
        plot_widget.clear()
        self.signal_index += self.ui.filtration_slider.value()
        if self.signal_index >= len(signal_data):
            self.signal_index = 0

        x_data = np.arange(self.signal_index)
        y_data = signal_data[: self.signal_index]
        y_max = max(y_data)
        y_min = min(y_data)

        plot_widget.plot(x=x_data, y=y_data, pen="orange")
        plot_widget.setYRange(y_min, y_max, padding=0.1)

        visible_range = (self.signal_index - 150, self.signal_index)
        x_min_limit, x_max_limit = 0, self.signal_index + 0.1

        plot_widget.setLimits(
            xMin=x_min_limit, xMax=x_max_limit, yMin=y_min, yMax=y_max
        )
        plot_widget.setXRange(*visible_range, padding=0)

    def update_filtration_rate(self):
        points_value = self.ui.filtration_slider.value()
        self.ui.speed_label.setText(f"Points: {points_value}")

    def pause_play_action(self, checked):
        if checked:
            self.plotting_timer.stop()
            self.ui.pause_play_button.setIcon(
                QtGui.QIcon("Resources/Icons/play_button.png")
            )
        else:
            self.plotting_timer.start(self.update_interval)
            self.ui.pause_play_button.setIcon(
                QtGui.QIcon("Resources/Icons/pause_button.png")
            )

    def apply_filter(self):
        if len(self.poles) == 0 and len(self.zeros) == 0:
            self.show_error(self.ui.emptyDesign, "Design is empty!")
            return
        self.filtered_data = signal.lfilter(
            self.numerator, self.denominator, self.original_data
        ).real
        self.signal_index = 0
        self.plotting_timer.start(self.update_interval)
        if self.ui.pause_play_button.isChecked():
            self.ui.pause_play_button.setChecked(False)

    # ORGANIZING ALL-PASS lIBRARY
    def organize_library(self, scrollAreaLayout, filtersList):
        for i, filter in enumerate(filtersList):
            scrollAreaLayout.addWidget(filter, i // 3, i % 3)

    def on_filter_chosen(self, checked, button):
        if checked:
            # Move the checked button from all_pass_filters to cascaded_filters
            if button in self.all_pass_filters:
                self.all_pass_filters.remove(button)
                self.cascaded_filters.append(button)
        else:
            # Move the unchecked button from cascaded_filters to all_pass_filters
            if button in self.cascaded_filters:
                self.cascaded_filters.remove(button)
                self.all_pass_filters.append(button)

        # Organize both libraries after the change
        self.organize_library(self.ui.gridLayout, self.all_pass_filters)
        self.organize_library(self.ui.gridLayoutForCascaded, self.cascaded_filters)

    def add_all_pass_filter(self):
        # Get the value entered in the text field
        value = self.ui.allPassEnteredValue.text()

        if not self.validate_a_value():
            self.user_inputs_values.append(value)

            # Instantiate a library button
            button_number = str(self.idx)
            button_name = f"allPass{button_number}"
            button = ProcessButton(value, self.idx)
            # Set the button name
            button.setObjectName(button_name)

            # Add the button to the cascaded filters
            self.cascaded_filters.append(button)

            # Set the button to checked initially
            button.setChecked(True)

            # Connect the button to the organizing library function
            button.toggled.connect(
                lambda checked, button=button: self.on_filter_chosen(checked, button)
            )

            # call the organize libraries function
            self.organize_library(self.ui.gridLayout, self.all_pass_filters)
            self.organize_library(self.ui.gridLayoutForCascaded, self.cascaded_filters)
            # Increment the index in case the user adds another custom filter
            self.idx += 1

    def validate_a_value(self):
        value = self.ui.allPassEnteredValue.text()

        if value in self.user_inputs_values:
            self.ui.allPassEnteredValue.setStyleSheet("border: 1px solid #ef0f2e;")
            self.show_error(self.ui.value_error, "Filter was already added")
            return True
        elif value == "":
            self.ui.allPassEnteredValue.setStyleSheet("border: 1px solid #ef0f2e;")
            self.show_error(self.ui.value_error, "Enter a value")
            return True
        elif value == "1":
            self.ui.allPassEnteredValue.setStyleSheet("border: 1px solid #ef0f2e;")
            self.show_error(self.ui.value_error, "'a' can't be 1")
            return True
        else:
            for filter in self.all_pass_filters + self.cascaded_filters:
                if complex(value) == complex(filter.allPassValue):
                    self.ui.allPassEnteredValue.setStyleSheet(
                        "border: 1px solid #ef0f2e;"
                    )
                    self.show_error(self.ui.value_error, "Filter already exists")
                    return True

        # If no duplicate is found, clear the error message and reset the border
        self.ui.allPassEnteredValue.setStyleSheet("")
        self.hide_error(self.ui.value_error)
        return False

    def plot_all_pass_zeros_and_poles(self):
        if len(self.cascaded_filters) == 0:
            self.show_error(self.ui.filterNotChosen, "Please, Pick a filter!")
            return
        else:
            # Iterate over the zeros positions and plot them
            for zero_position in self.all_pass_zeros_positions:
                item = TargetItem(
                    pos=zero_position,
                    size=10,
                    movable=False,
                    symbol="o",
                    pen=pg.mkPen("g"),
                )
                self.ui.unitCirclePlot.addItem(item)
            # Iterate over the poles positions and plot them
            for pole_position in self.all_pass_poles_positions:
                item = TargetItem(
                    pos=pole_position,
                    size=10,
                    movable=False,
                    symbol="x",
                    pen=pg.mkPen("r"),
                )
                self.ui.unitCirclePlot.addItem(item)

    # GENERATE SIGNAL BY MOUSE MOVEMENT
    def start_generating(self, checked):
        if checked:
            self.plotting_timer.stop()
            self.ui.originalApplicationSignal.clear()
            self.ui.filteredSignal.clear()
            self.original_data = []
            self.filtered_data = []
            self.ui.mousePad.frequencySignal.connect(self.capture_mouse_signal)
        else:
            self.ui.mousePad.frequencySignal.disconnect(self.capture_mouse_signal)

    def capture_mouse_signal(self, frequency, y):
        self.original_data.append(y)
        self.filtered_data = [0] + self.original_data
        self.mouse_signal_frequencies.append(frequency)
        self.apply_filter()
        # Update the real-time plots
        self.update_real_time_plots()
