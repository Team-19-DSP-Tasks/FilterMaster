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
from scipy.signal import freqz, lfilter, zpk2tf

# A folder to store the phase response plots of all-pass filters
save_directory = "Resources/All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)


class Backend:
    def __init__(self, ui):
        self.ui = ui

        # UI Objects to Methods Connections
        self.ui.addPole.clicked.connect(lambda: self.pole_mode())
        self.ui.addZero.clicked.connect(lambda: self.zero_mode())

        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            lambda event: self.handle_unit_circle_click(event)
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

    # VALIDATING INPUT

    # HELPER FUNCTIONS TO AVOID CODE REPETITION
    def add_target_item(self, pos, symbol, color):
        """
        It just add A ZERO OR POLE TO THE UNIT CIRCLE.
        """
        item = TargetItem(
            pos=pos,
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        self.ui.unitCirclePlot.addItem(item)
        return item

    # MAIN FUNCTION
    def handle_unit_circle_click(self, event):
        # Get the clicked position by mouse
        pos = self.ui.unitCirclePlot.mapToView(event.scenePos())

        # Check which button is clicked to determine whether to add or remove
        if event.button() == QtCore.Qt.LeftButton:
            if self.is_pole:
                item = self.add_target_item(pos, "x", "r")
                self.store_drawn_item(
                    pos,
                    item,
                    self.poles,
                    self.poles_positions,
                    self.poles_conjugates,
                    self.poles_conjugates_positions,
                )
            elif self.is_zero:
                item = self.add_target_item(pos, "o", "r")
                self.store_drawn_item(
                    pos,
                    item,
                    self.zeros,
                    self.zeros_positions,
                    self.zeros_conjugates,
                    self.zeros_conjugates_positions,
                )

            # if self.ui.addConjugatesCheckBox.isChecked():
            #     if self.is_pole:
            #         self.draw_conjugates(
            #             [self.poles_conjugates_positions[-1]], "x", "b"
            #         )
            #     elif self.is_zero:
            #         self.draw_conjugates(
            #             [self.zeros_conjugates_positions[-1]], "o", "y"
            #         )

        elif event.button() == QtCore.Qt.RightButton:
            self.create_context_menu(pos)

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
        # self.update_responses()

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

        # self.update_responses()

    # REMOVE ALL ZEROS/POLES AND RESET DESIGN

    # REMOVE A SPECIFIC ZERO OR POLE

    # HANDLING CONJUGATES

    # EXPORT THE DESIGNED FILTER

    # PLOT MAGNITUDE AND PHASE RESPONSES

    # APPLICATION SIGNALS PLOTTING

    # ORGANIZING ALL-PASS lIBRARY

    # GENERATE SIGNAL BY MOUSE MOVEMENT
