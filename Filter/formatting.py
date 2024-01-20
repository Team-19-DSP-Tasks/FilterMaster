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
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph import TargetItem
from scipy import signal
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

        ## === Exporting === ##
        self.ui.exportSignal.clicked.connect(lambda: self.export_signal())
        self.ui.exportFilter.clicked.connect(lambda: self.export_filter())

        ## === CUSTOM ALL-PASS CREATION === ##
        self.ui.addAllPassFilter.clicked.connect(lambda: self.add_all_pass_filter())
        self.ui.allPassEnteredValue.editingFinished.connect(
            lambda: self.add_all_pass_filter()
        )

        ## === APPLYING FILTERS === ##
        self.ui.applyFilterButton.clicked.connect(lambda: self.apply_filter())
        self.ui.correctPhase.clicked.connect(lambda: self.correct_phase())

        ## === Z-Plane Clicking === ##
        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: self.handle_unit_circle_click(event)
        )

        ## === Conjugates === ##
        self.ui.addConjugatesCheckBox.stateChanged.connect(
            lambda: self.handle_conjugates()
        )

        ## === PAUSE AND PLAY === ##
        self.ui.pause_play_button.toggled.connect(
            lambda checked: self.pause_play_action(checked)
        )
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

        # For All-Pass zeros and poles plotting
        self.all_pass_zeros = []
        self.all_pass_poles = []
        self.all_pass_zeros_items = []
        self.all_pass_poles_items = []

        # For plotting magnitude and phase responses of Z-Plane Filter
        self.mag_curve = pg.PlotCurveItem(pen="b")
        self.phase_curve = pg.PlotCurveItem(pen="r")

        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.magFrequencyResponse.addItem(self.mag_curve)
        self.ui.phaseFrequencyResponse.addItem(self.phase_curve)

        # For plotting cascaded filter phase response
        self.all_pass_phase_curve = pg.PlotCurveItem(pen="r")

        # Add PlotCurveItem to magnitude and phase response plots
        self.ui.allPassPhaseResponse.addItem(self.all_pass_phase_curve)

        # Variables for real time plotting
        self.update_interval = 50
        self.plotting_timer = QTimer()
        self.plotting_timer.timeout.connect(self.update_real_time_plots)
        self.plotting_timer.start(self.update_interval)
        self.signal_index = 0

        # Data storing variables to be plotted: initially defined
        self.original_data = []
        self.filtered_data = self.original_data

        # All-Pass Library
        self.user_inputs_values = []
        self.idx = 9  # to accurately name the plot response of all-pass filter
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

    # PLOT MAGNITUDE AND PHASE RESPONSES
    def update_responses(self):
        # Get poles and zeros positions
        zeros_array = np.array([complex(z.x(), z.y()) for z in self.zeros_positions])
        poles_array = np.array([complex(p.x(), p.y()) for p in self.poles_positions])

        # Calculate magnitude and phase responses
        numerator, denominator = zpk2tf(zeros_array, poles_array, 1)
        frequencies_values, response_complex = freqz(numerator, denominator)

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
                    writer.writerow([])
                    for allpass_zero in self.all_pass_zeros:
                        writer.writerow(
                            [
                                "allpass_zero",
                                allpass_zero.pos().x(),
                                allpass_zero.pos().y(),
                            ]
                        )
                    writer.writerow([])
                    for allpass_pole in self.all_pass_poles:
                        writer.writerow(
                            [
                                "allpass_pole",
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
                self.update_plot()  # Use the new signal data for real-time plotting
                self.plotting_timer.start(self.update_interval)
            except Exception as e:
                print(f"Error loading the file: {e}")

    def update_real_time_plots(self):
        pass

    def update_plot(self):
        pass

    def update_filtration_rate(self):
        pass

    def pause_play_action(self):
        pass

    def apply_filter(self):
        pass

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
                self.remove_all_pass_zeros_and_poles()
                self.add_all_pass_zeros_and_poles()
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

            # Plot the phase response of the all-pass filter
            plot_image_path = self.store_all_pass_response(value)

            # Instantiate a library button
            button_number = str(self.idx)
            button_name = f"allPass0{button_number}"
            button_text = f"a = {value}"
            button = ProcessButton(button_text, plot_image_path, value)
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
            self.show_error(self.ui.value_error, "Filter was already added")
            return True
        elif value == "":
            self.show_error(self.ui.value_error, "Enter a value")
            return True
        elif value == "0":
            self.show_error(self.ui.value_error, "'a' can't be 0")
            return True
        elif value == "1":
            self.show_error(self.ui.value_error, "'a' can't be 1")
            return True
        else:
            for filter in self.all_pass_filters + self.cascaded_filters:
                if complex(value) == complex(filter.allPassValue):
                    self.show_error(self.ui.value_error, "Filter already exists")
                    return True

        # If no duplicate is found, clear the error message and reset the border
        self.hide_error(self.ui.value_error)
        return False

    def store_all_pass_response(self, value):
        a_complex = complex(value)

        pole = a_complex
        self.all_pass_poles.append(pole)
        zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
        self.all_pass_zeros.append(zero)

        # Calculate frequency response using freqz
        numerator, denominator = signal.zpk2tf(
            self.all_pass_zeros, self.all_pass_poles, 1
        )
        all_pass_frequencies_values, all_pass_response_complex = signal.freqz(
            numerator, denominator, worN=8000
        )

        # Plot the phase response
        plt.figure()
        plt.plot(
            all_pass_frequencies_values,
            np.unwrap(np.angle(all_pass_response_complex)),
            color="orange",
            linewidth=5,
        )
        plt.axis("off")
        # Save the plot as a PNG file
        save_path = os.path.join(save_directory, f"phase_response_{self.idx}.png")
        plt.savefig(save_path, transparent=True)
        plt.clf()
        return save_path

    def add_all_pass_zeros_and_poles(self):
        # Iterate over the zeros positions and plot them
        for zero in self.all_pass_zeros:
            item = self.add_target_item((zero.real, zero.imag), False, "o", "orange")
            self.all_pass_zeros_items.append(item)

        # Iterate over the poles positions and plot them
        for pole in self.all_pass_poles:
            item = self.add_target_item((pole.real, pole.imag), False, "x", "orange")
            self.all_pass_poles_items.append(item)

    def remove_all_pass_zeros_and_poles(self):
        for zero_item in self.all_pass_zeros_items:
            self.ui.unitCirclePlot.removeItem(zero_item)
        for pole_item in self.all_pass_poles_items:
            self.ui.unitCirclePlot.removeItem(pole_item)

    def correct_phase(self):
        if len(self.cascaded_filters) == 0:
            self.show_error(self.ui.filterNotChosen, "Please, Pick a filter!")
            return
        else:
            pass

    # GENERATE SIGNAL BY MOUSE MOVEMENT
    def start_generating(self, checked):
        pass

    def capture_mouse_signal(self, frequency, y):
        pass

    # VALIDATING INPUT & ERROR MESSAGES
    def show_error(self, error_label, message):
        self.ui.allPassEnteredValue.setStyleSheet("border: 1px solid #ef0f2e;")
        error_label.setText(f'<font color="#ef0f2e">{message}</font>')
        error_label.setVisible(True)

    def hide_error(self, error_label):
        self.ui.allPassEnteredValue.setStyleSheet("")
        error_label.clear()
        error_label.setVisible(False)