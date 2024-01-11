import csv
import logging
import sys

import numpy as np
import pandas as pd
import pyqtgraph as pg
import scipy
import wfdb
from PyQt5 import QtCore
from PyQt5.QtWidgets import QFileDialog

logging.basicConfig(
    level=logging.DEBUG,
    filename="log.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add an empty line to the log file
with open("log.log", "a") as log_file:
    log_file.write("\n")


# Global Variables for creating and storing poles and zeros
isPole = False
isZero = False
polePositions = []  # first added positions
zeroPositions = []  # first added positions
poleConjugates = []  # conjugates to the added positions
zeroConjugates = []  # conjugates to the added positions
poles = []  # combination of conjugates and the clicked positions
zeros = []  # combination of conjugates and the clicked positions

# Global Variables for real time plotting
signalIndex = 0
imported_data = None


##### Creating Zeros or Poles #####
###################################
def create_pole():
    global isPole, isZero
    isPole = True
    isZero = False
    logging.info(f"isPole = {isPole}")


def create_zero():
    global isPole, isZero
    isZero = True
    isPole = False
    logging.info(f"isZero = {isZero}")


def create(x, y, addConjugatesCheckBox, unitCirclePlot):
    global isPole, isZero
    if isPole:
        logging.info(f"Adding Pole at Coordinates --> x:{x}, y:{y}")
        polePositions.append((x, y))
    elif isZero:
        logging.info(f"Adding Zero at Coordinates --> x:{x}, y:{y}")
        zeroPositions.append((x, y))

    # Call addConjugates if the checkbox is checked
    if addConjugatesCheckBox.isChecked():
        addConjugates(addConjugatesCheckBox, unitCirclePlot)


def handleUnitCircleClick(event, unitCirclePlot, addConjugatesCheckBox):
    global polePositions, zeroPositions
    # Get the coordinates of the mouse click
    if event.button() == QtCore.Qt.LeftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
        x, y = pos.x(), pos.y()
        # Add a symbol at the clicked position based on the current mode
        if isPole:
            symbol = "x"
            color = "b"
        elif isZero:
            symbol = "o"
            color = "g"

        # Add the symbol to the unitCirclePlot
        symbol_item = pg.ScatterPlotItem(
            size=10,
            symbol=symbol,
            pen=pg.mkPen(None),
            brush=pg.mkBrush(color),
        )
        symbol_item.addPoints(x=[x], y=[y])
        unitCirclePlot.addItem(symbol_item)

        # Log the click coordinates and add to the corresponding list
        create(x, y, addConjugatesCheckBox, unitCirclePlot)
        logging.debug(f"poles: {polePositions}")
        logging.debug(f"zeros: {zeroPositions}")


##### Deleting Zeros or Poles or Both #####
###########################################
def removeSymbolsByType(unitCirclePlot, symbolType=None):
    global polePositions, zeroPositions
    # Remove symbols of the specified type or all symbols if type is None
    for item in unitCirclePlot.items():
        if isinstance(item, pg.ScatterPlotItem) and (
            symbolType is None or item.opts["symbol"] == symbolType
        ):
            unitCirclePlot.removeItem(item)

    # Reset the corresponding positions list if a specific type is provided
    if symbolType == "x":
        polePositions = []
    elif symbolType == "o":
        zeroPositions = []
    else:
        polePositions = []
        zeroPositions = []


def removePoles(unitCirclePlot):
    removeSymbolsByType(unitCirclePlot, "x")


def removeZeros(unitCirclePlot):
    removeSymbolsByType(unitCirclePlot, "o")


def reset(unitCirclePlot):
    removeSymbolsByType(unitCirclePlot, None)


##### Add Conjugates #####
##########################
def drawConjugates(unitCirclePlot, conjugates, symbol, color):
    for x, y in conjugates:
        symbol_item = pg.ScatterPlotItem(
            size=10,
            symbol=symbol,
            pen=pg.mkPen(None),
            brush=pg.mkBrush(color),
        )
        symbol_item.addPoints(x=[x], y=[y])
        unitCirclePlot.addItem(symbol_item)


def addConjugates(addConjugatesCheckBox, unitCirclePlot):
    global polePositions, zeroPositions, poleConjugates, zeroConjugates
    if addConjugatesCheckBox.isChecked():
        # Create new lists for conjugates
        poleConjugates = [(x[0], -x[1]) for x in polePositions]
        zeroConjugates = [(x[0], -x[1]) for x in zeroPositions]

        # Draw pole conjugates
        drawConjugates(unitCirclePlot, poleConjugates, "x", "r")

        # Draw zero conjugates
        drawConjugates(unitCirclePlot, zeroConjugates, "o", "y")

        logging.debug(f"polesConj: {poleConjugates}\nzerosConj: {zeroConjugates}")


# Predefined Real Time Plotting
def updatePlot(originalApplicationSignal, data):
    global signalIndex
    originalApplicationSignal.clear()
    signalIndex += 1
    if signalIndex >= len(data):
        signalIndex = 0
    x_data = np.arange(signalIndex)
    y_data = data[:signalIndex]
    y_max = max(y_data)
    y_min = min(y_data)
    originalApplicationSignal.plot(x=x_data, y=y_data, pen="orange")
    originalApplicationSignal.setYRange(y_min, y_max, padding=0.1)
    # Calculate the visible range for the X-axis based on the current signal_index_1
    visible_range = (signalIndex - 150, signalIndex)
    # Set the X-axis limits to control the visible range
    x_min_limit = 0
    x_max_limit = signalIndex + 0.1
    originalApplicationSignal.setLimits(
        xMin=x_min_limit, xMax=x_max_limit, yMin=y_min, yMax=y_max
    )
    originalApplicationSignal.setXRange(*visible_range, padding=0)


# Import a signal
def importSignal(originalApplicationSignal):
    global imported_data, timer
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
                imported_data = record.p_signal[:, 0]  # Use the first channel

            elif file_path.endswith(".csv"):
                # Use pandas to read the CSV file
                data_frame = pd.read_csv(file_path)
                # Use the first column as the signal data
                imported_data = data_frame.iloc[:, 0].to_numpy()
            else:
                pass
            print("accessed")
            updatePlot(originalApplicationSignal, imported_data)
        except Exception as e:
            print(f"Error loading the file: {e}")


# Plot the imported signal

# Generate signal by your mouse movement
