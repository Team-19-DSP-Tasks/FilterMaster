import csv
import os

import numpy as np
import pandas as pd
import pyqtgraph as pg
import wfdb
from Classes.libraryButton import ProcessButton
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPointF, QTimer
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph import TargetItem
from scipy.signal import freqz, lfilter, zpk2tf

# A folder to store the phase response plots of all-pass filters
save_directory = "Resources/All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)


class Backend:
    def __init__(self, ui):
        self.ui = ui

        # UI Objects to Methods Connections
        ## === Creating === ##
        self.ui.addPole.clicked.connect(lambda: self.pole_mode())
        self.ui.addZero.clicked.connect(lambda: self.zero_mode())

        ## === Removing === ##
        self.ui.removeAllPoles.clicked.connect(lambda: self.remove_poles())
        self.ui.removeAllZeros.clicked.connect(lambda: self.remove_zeros())
        self.ui.resetDesign.clicked.connect(lambda: self.reset_design())

        ## === IMPORTING === ##
        self.ui.actionImport_Signal.triggered.connect(self.import_signal)
        self.ui.zPlane_dock_widget.csvDropped.connect(self.import_filter)

        ## === Exporting === ##
        self.ui.exportSignal.clicked.connect(lambda: self.export_signal())
        self.ui.exportFilter.clicked.connect(lambda: self.export_filter())

        ## === CUSTOM ALL-PASS CREATION === ##
        self.ui.addAllPassFilter.clicked.connect(
            lambda: self.customize_all_pass_filter()
        )
        self.ui.gainInput.returnPressed.connect(
            lambda: self.customize_all_pass_filter()
        )

        ## === APPLYING FILTERS === ##
        self.ui.applyFilterButton.clicked.connect(lambda: self.apply_filter())
        self.ui.correctPhase.clicked.connect(lambda: self.correct_phase())

        ## === Z-Plane Clicking === ##
        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: self.handle_unit_circle_click(event)
        )

        ## === Examples Menu Options === ##
        self.ui.actionHighPass.triggered.connect(
            lambda: self.import_filter(self.ui.highpass_zeros, [], [], [])
        )
        self.ui.actionLowPass.triggered.connect(
            lambda: self.import_filter([], self.ui.lowpass_poles, [], [])
        )
        self.ui.actionBandPass.triggered.connect(
            lambda: self.import_filter(self.ui.bandpass_zeros, [], [], [])
        )

        ## === Conjugates === ##
        self.ui.addConjugatesCheckBox.stateChanged.connect(
            lambda: self.handle_conjugates()
        )

        ## === PAUSE AND PLAY === ##
        self.ui.pause_play_button.toggled.connect(
            lambda checked: self.pause_play_action(checked)
        )

        ## === RESET PLOTTING === ##
        self.ui.resetSignal.clicked.connect(self.reset_signal)

        ## === CHANGE FILTRATION RATE === ##
        self.ui.filtration_slider.valueChanged.connect(
            lambda: self.update_filtration_rate()
        )

        ## === SIGNAL GENERATION === ##
        self.ui.generateSignal.toggled.connect(
            lambda checked: self.start_generating(checked)
        )

        # To control poles and zeros creation
        self.ui.addZero.setChecked(True)
        self.is_zero = True  # initially, add zeros
        self.is_pole = False

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

        # For Z-Plane Filter Storing
        self.numerator = None
        self.denominator = None

        # For All-Pass zeros and poles plotting
        self.all_pass_zeros = []
        self.all_pass_poles = []

        # For plotting magnitude and phase responses of Z-Plane Filter
        self.mag_curve = pg.PlotCurveItem(pen="b")
        self.phase_curve = pg.PlotCurveItem(pen="r")

        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.magFrequencyResponse.addItem(self.mag_curve)
        self.ui.phaseFrequencyResponse.addItem(self.phase_curve)

        # For plotting cascaded filter phase response
        self.all_pass_phase_curve = pg.PlotCurveItem(pen="orange", linewidth=5)

        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.allPassPhaseResponse.addItem(self.all_pass_phase_curve)

        # Cascaded All-Pass Transfer Function
        self.cascaded_numerator = None
        self.cascaded_denominator = None

        # Variables for real time plotting
        self.update_interval = 50
        self.plotting_timer = QTimer()
        self.plotting_timer.timeout.connect(self.update_real_time_plots)
        self.signal_index = 0

        self.slicing_idx = 0
        self.applying_timer = QTimer()
        self.applying_timer.timeout.connect(self.slice_data)

        # Data storing variables to be plotted: initially defined
        self.original_data = []
        self.filtered_data = []

        # Not to reset mouse signal
        self.mouse_signal = False

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

    # HELPER FUNCTIONS TO AVOID CODE REPETITION
    def add_target_item(self, pos, movable, symbol, color):
        """
        It just add A ZERO OR POLE TO THE UNIT CIRCLE.
        """
        item = TargetItem(
            pos=pos,
            size=10,
            movable=movable,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        self.ui.unitCirclePlot.addItem(item)
        return item

    # MAIN FUNCTION FOR Z-PLANE
    def handle_unit_circle_click(self, event):
        # Get the clicked position by mouse
        pos = self.ui.unitCirclePlot.mapToView(event.scenePos())

        # Check which button is clicked to determine whether to add or remove
        if event.button() == QtCore.Qt.LeftButton:
            if self.is_pole:
                item = self.add_target_item(pos, True, "x", "r")
                self.store_drawn_item(
                    pos,
                    item,
                    self.poles,
                    self.poles_positions,
                    self.poles_conjugates,
                    self.poles_conjugates_positions,
                )
            elif self.is_zero:
                item = self.add_target_item(pos, True, "o", "g")
                self.store_drawn_item(
                    pos,
                    item,
                    self.zeros,
                    self.zeros_positions,
                    self.zeros_conjugates,
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
            self.ui.remove_action.triggered.connect(lambda: self.remove_item(pos))
            self.ui.context_menu.exec_(QtGui.QCursor.pos())

    # CREATING ZEROS AND POLES
    def zero_mode(self):
        self.is_pole = False
        self.is_zero = True
        self.ui.addPole.setChecked(False)

    def pole_mode(self):
        self.is_pole = True
        self.is_zero = False
        self.ui.addZero.setChecked(False)

    def store_drawn_item(
        self,
        pos,
        item,
        items,
        positions_list,
        conjugates_list,
        conjugates_positions_list,
    ):
        items.append(item)
        positions_list.append(pos)
        conjugates_positions_list.append(pg.Point(pos.x(), -pos.y()))
        index = positions_list.index(pos)
        # Connect the sigPositionChanged signal to the update_positions function
        item.sigPositionChanged.connect(
            lambda: self.update_positions_on_moving(
                item,
                index,
                positions_list,
                conjugates_list,
                conjugates_positions_list,
            )
        )
        # Update the magnitude and phase plotting if items are being moved
        self.update_responses()

    def update_positions_on_moving(
        self,
        item,
        index,
        positions_list,
        conjugates_list,
        conjugates_positions_list,
    ):
        new_pos = item.pos()
        positions_list[index] = new_pos
        conjugates_positions_list[index] = pg.Point(new_pos.x(), -new_pos.y())
        if bool(conjugates_list):
            conjugates_list[index].setPos(conjugates_positions_list[index])

        self.update_responses()

    def import_filter(self, zeros, poles, allpass_zeros, allpass_poles):
        # Reset everything
        self.reset_design()
        for filter in self.cascaded_filters:
            self.remove_all_pass_zeros_and_poles(
                self.all_pass_zeros, filter.zero.real, filter.zero.imag
            )
            self.remove_all_pass_zeros_and_poles(
                self.all_pass_poles, filter.pole.real, filter.pole.imag
            )

        # Plot the imported filters
        for zero_pos in zeros:
            item = self.add_target_item(zero_pos, True, "o", "g")
            self.store_drawn_item(
                zero_pos,
                item,
                self.zeros,
                self.zeros_positions,
                self.zeros_conjugates,
                self.zeros_conjugates_positions,
            )
        for pole_pos in poles:
            item = self.add_target_item(pole_pos, True, "x", "r")
            self.store_drawn_item(
                pole_pos,
                item,
                self.poles,
                self.poles_positions,
                self.poles_conjugates,
                self.poles_conjugates_positions,
            )
        self.handle_conjugates()

        self.update_responses()

    # PLOT MAGNITUDE AND PHASE RESPONSES
    def update_responses(self):
        # Get poles and zeros positions
        zeros_array = np.array([complex(z.x(), z.y()) for z in self.zeros_positions])
        poles_array = np.array([complex(p.x(), p.y()) for p in self.poles_positions])

        # Calculate magnitude and phase responses
        self.numerator, self.denominator = zpk2tf(zeros_array, poles_array, 1)
        frequencies_values, response_complex = freqz(self.numerator, self.denominator)

        # Update magnitude response plot
        self.mag_curve.setData(frequencies_values, 20 * np.log10(abs(response_complex)))

        # Update phase response plot
        self.phase_curve.setData(frequencies_values, np.angle(response_complex))

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

    # REMOVE A SPECIFIC ZERO OR POLE
    def remove_item_helper(
        self, clicked_position, items, positions, conjugates, conjugates_positions
    ):
        tolerance = 0.1
        for pos in positions:
            if (pos - clicked_position).manhattanLength() < tolerance:
                index = positions.index(pos)
                item = items[index]
                self.ui.unitCirclePlot.removeItem(item)
                items.remove(item)
                positions.remove(pos)
                conjugates_positions.remove(conjugates_positions[index])
                if self.ui.addConjugatesCheckBox.isChecked():
                    self.ui.unitCirclePlot.removeItem(conjugates[index])
                    conjugates.remove(conjugates[index])

    def remove_item(self, clicked_position):
        self.remove_item_helper(
            clicked_position,
            self.poles,
            self.poles_positions,
            self.poles_conjugates,
            self.poles_conjugates_positions,
        )
        self.remove_item_helper(
            clicked_position,
            self.zeros,
            self.zeros_positions,
            self.zeros_conjugates,
            self.zeros_conjugates_positions,
        )

        self.update_responses()

    # HANDLING CONJUGATES
    def handle_conjugates(self):
        if self.ui.addConjugatesCheckBox.isChecked():
            self.draw_conjugates(self.poles_conjugates_positions, "x", "b")
            self.draw_conjugates(self.zeros_conjugates_positions, "o", "y")
        else:
            self.remove(self.poles_conjugates + self.zeros_conjugates)
            self.poles_conjugates.clear()
            self.zeros_conjugates.clear()

    def draw_conjugates(self, conjugates_positions, symbol, color):
        for pos in conjugates_positions:
            item = self.add_target_item(pos, False, symbol, color)
            if symbol == "x":
                self.poles_conjugates.append(item)
            elif symbol == "o":
                self.zeros_conjugates.append(item)

    # EXPORT THE DESIGNED FILTER
    def export_filter(self):
        if len(self.poles) == 0 and len(self.zeros) == 0:
            self.show_error(
                self.ui.emptyDesign, "Design is empty!", self.ui.exportFilter
            )
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
                    writer.writerow([])
                    for allpass_zero in self.all_pass_zeros:
                        writer.writerow(
                            [
                                "allpass zero",
                                allpass_zero.pos().x(),
                                allpass_zero.pos().y(),
                            ]
                        )
                    writer.writerow([])
                    for allpass_pole in self.all_pass_poles:
                        writer.writerow(
                            [
                                "allpass pole",
                                allpass_pole.pos().x(),
                                allpass_pole.pos().y(),
                            ]
                        )

    # EXPORT THE FILTERED SIGNAL
    def export_signal(self):
        fileName, _ = QFileDialog.getSaveFileName(
            None, "Save File", "", "CSV Files (*.csv)"
        )
        if fileName:
            np.savetxt(fileName, self.filtered_data, delimiter=",")

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
                self.add_all_pass_zeros_and_poles(button)
                self.update_cascaded_phase_response()
                self.update_z_plane_view()
        else:
            # Move the unchecked button from cascaded_filters to all_pass_filters
            if button in self.cascaded_filters:
                self.cascaded_filters.remove(button)
                self.all_pass_filters.append(button)
                self.remove_all_pass_zeros_and_poles(
                    self.all_pass_zeros, button.zero.real, button.zero.imag
                )
                self.remove_all_pass_zeros_and_poles(
                    self.all_pass_poles, button.pole.real, button.pole.imag
                )
                self.update_cascaded_phase_response()
                self.update_z_plane_view()

        # Organize both libraries after the change
        self.organize_library(self.ui.gridLayout, self.all_pass_filters)
        self.organize_library(self.ui.gridLayoutForCascaded, self.cascaded_filters)

    def customize_all_pass_filter(self):
        # Get the value entered in the text field
        value = self.ui.gainInput.text()
        if not self.validate_a_value():
            self.user_inputs_values.append(value)
            self.ui.gainInput.clear()

            # Instantiate a library button
            button_number = str(self.idx)
            button_name = f"allPass{button_number}"
            button = ProcessButton(value, self.idx, self.ui.scrollAreaWidgetContents)
            # Set the button name
            button.setObjectName(button_name)

            # Add the button to the cascaded filters
            self.cascaded_filters.append(button)
            self.add_all_pass_zeros_and_poles(button)
            self.update_cascaded_phase_response()

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
        value = self.ui.gainInput.text()

        if value in self.user_inputs_values:
            self.show_error(
                self.ui.value_error,
                "Filter was already added",
                self.ui.gainInput,
            )
            return True
        elif value == "":
            self.show_error(self.ui.value_error, "Enter a value", self.ui.gainInput)
            return True
        elif value == "0":
            self.show_error(self.ui.value_error, "'a' can't be 0", self.ui.gainInput)
            return True
        elif value == "1":
            self.show_error(self.ui.value_error, "'a' can't be 1", self.ui.gainInput)
            return True
        else:
            for filter in self.all_pass_filters + self.cascaded_filters:
                if complex(value) == complex(filter.allPassValue):
                    self.show_error(
                        self.ui.value_error,
                        "Filter already exists",
                        self.ui.gainInput,
                    )
                    return True

        # If no duplicate is found, clear the error message and reset the border
        self.hide_error(self.ui.value_error)
        return False

    def add_all_pass_zeros_and_poles(self, button):
        zero_item = self.add_target_item(
            (button.zero.real, button.zero.imag), False, "o", "orange"
        )
        pole_item = self.add_target_item(
            (button.pole.real, button.pole.imag), False, "x", "orange"
        )
        self.all_pass_zeros.append(zero_item)
        self.all_pass_poles.append(pole_item)

    def remove_all_pass_zeros_and_poles(self, items, real, imag):
        for item in items:
            if item.pos() == QPointF(real, imag):
                self.ui.unitCirclePlot.removeItem(item)
                items.remove(item)

    def update_z_plane_view(self):
        max_value = 1.1
        for item in self.all_pass_zeros + self.all_pass_poles:
            max_value = max(max_value, item.pos().x())
            max_value = max(max_value, item.pos().y())

        max_value += 0.2  # to make the plane visually appealing
        self.ui.unitCirclePlot.setRange(
            xRange=(-max_value, max_value), yRange=(-max_value, max_value)
        )
        self.ui.unitCirclePlot.setLimits(
            xMin=-max_value, xMax=max_value, yMin=-max_value, yMax=max_value
        )

    def update_cascaded_phase_response(self):
        self.cascaded_numerator = np.array([1.0])
        self.cascaded_denominator = np.array([1.0])
        for filter in self.cascaded_filters:
            numerator, denominator = filter.get_transfer_function()
            self.cascaded_numerator, self.cascaded_denominator = np.convolve(
                self.cascaded_numerator, numerator
            ), np.convolve(self.cascaded_denominator, denominator)

        # Plot the phase response of the cascaded filter
        cascade_frequencies, cascade_response = freqz(
            self.cascaded_numerator, self.cascaded_denominator, worN=8000
        )

        self.all_pass_phase_curve.setData(
            cascade_frequencies,
            np.unwrap(np.angle(cascade_response)),
        )

    def correct_phase(self):
        if len(self.cascaded_filters) == 0:
            self.show_error(
                self.ui.filterNotChosen,
                "Please, Pick a filter or make one!",
                self.ui.correctPhase,
            )
            self.update_responses(),
            return
        else:
            self.hide_error(self.ui.filterNotChosen)
            corrected_numerator, corrected_denominator = np.convolve(
                self.cascaded_numerator, self.numerator
            ), np.convolve(self.cascaded_denominator, self.denominator)
            corrected_frequencies, corrected_response = freqz(
                corrected_numerator, corrected_denominator, worN=8000
            )
            self.phase_curve.setData(
                corrected_frequencies,
                np.unwrap(np.angle(corrected_response)),
            )

    # VALIDATING INPUT & ERROR MESSAGES
    def show_error(self, error_label, message, widget):
        widget.setStyleSheet("border: 1px solid orange;")
        error_label.setText(f'<font color="orange">{message}</font>')
        error_label.setVisible(True)

    def hide_error(self, error_label):
        self.ui.gainInput.setStyleSheet("")
        error_label.clear()
        error_label.setVisible(False)

    # APPLICATION SIGNALS Importing & PLOTTING
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
                self.update_real_time_plots()  # Use the new signal data for real-time plotting
                self.plotting_timer.start(self.update_interval)
            except Exception as e:
                print(f"Error loading the file: {e}")

    def update_real_time_plots(self):
        self.update_plot(self.ui.originalSignalPlot, self.original_data)
        self.update_plot(self.ui.filteredSignalPlot, self.filtered_data)

    def update_plot(self, plot_widget, signal_data):
        plot_widget.clear()
        self.signal_index += (
            self.ui.filtration_slider.value()
        )  # Increment by the value of the slider
        if self.signal_index >= len(signal_data):
            self.signal_index = len(signal_data)
            # self.signal_index = len(signal_data)  # Reset the signal index to 0
            # self.plotting_timer.stop()

        x_data = np.arange(self.signal_index)
        y_data = signal_data[: self.signal_index]
        y_max = max(signal_data)
        y_min = min(signal_data)

        plot_widget.plot(x=x_data, y=y_data, pen="orange")
        plot_widget.setYRange(y_min, y_max, padding=0.1)

        visible_range = (self.signal_index - 150, self.signal_index + 150)
        x_min_limit, x_max_limit = 0, self.signal_index + 0.1

        plot_widget.setLimits(
            xMin=x_min_limit, xMax=x_max_limit, yMin=y_min, yMax=y_max
        )
        plot_widget.setXRange(*visible_range, padding=0)

    def update_filtration_rate(self):
        points_value = self.ui.filtration_slider.value()
        self.ui.filtration_label.setText(f"Filtered Points: {points_value}")

    def pause_play_action(self, checked):
        if checked:
            self.plotting_timer.stop()
            self.applying_timer.stop()  # Also stop the applying_timer
            self.ui.pause_play_button.setIcon(
                QtGui.QIcon("Resources/Icons/play_button.png")
            )
        else:
            self.plotting_timer.start(self.update_interval)
            if len(self.poles) != 0 and len(self.zeros) != 0:
                self.applying_timer.start(
                    self.update_interval
                )  # Also start the applying_timer
            self.ui.pause_play_button.setIcon(
                QtGui.QIcon("Resources/Icons/pause_button.png")
            )

    def reset_signal(self):
        self.plotting_timer.stop()
        self.applying_timer.stop()
        self.ui.originalSignalPlot.clear()
        self.ui.filteredSignalPlot.clear()
        self.signal_index = 0
        self.slicing_idx = 0
        self.plotting_timer.start(self.update_interval)

    def slice_data(self):
        points = self.ui.filtration_slider.value()
        # chunk is the end of the slice
        chunk = self.slicing_idx + points
        # if chunk > len(self.original_data):
        #     self.applying_timer.stop()
        #     self.apply_filter()  # Restart the filtration and plotting
        #     return
        self.filtered_data = np.append(
            self.filtered_data,
            lfilter(
                self.numerator,
                self.denominator,
                self.original_data[self.slicing_idx : chunk],
            ).real,
        )

        # self.update_real_time_plots()
        self.slicing_idx += points

    def apply_filter(self):
        if len(self.poles) == 0 and len(self.zeros) == 0:
            self.show_error(
                self.ui.emptyDesign, "Design is empty!", self.ui.applyFilterButton
            )
            return
        self.ui.generateSignal.setChecked(False)
        self.ui.filtration_slider.setValue(len(self.poles) + len(self.zeros))

        # Reset parameters
        self.signal_index = 0
        self.slicing_idx = 0
        self.filtered_data = np.array([])

        # Restart timers
        self.plotting_timer.start(self.update_interval)
        self.applying_timer.start(self.update_interval)

        if self.ui.pause_play_button.isChecked():
            self.ui.pause_play_button.setChecked(False)

    # GENERATE SIGNAL BY MOUSE MOVEMENT
    def start_generating(self, checked):
        if checked:
            self.plotting_timer.stop()
            self.ui.originalSignalPlot.clear()
            self.ui.filteredSignalPlot.clear()
            self.original_data = []
            self.filtered_data = []
            self.ui.mousePad.dataPoint.connect(self.capture_mouse_signal)
        else:
            self.ui.mousePad.dataPoint.disconnect(self.capture_mouse_signal)

    def capture_mouse_signal(self, y):
        self.original_data.append(y)
        self.filtered_data.append(y)
        self.update_real_time_plots()
