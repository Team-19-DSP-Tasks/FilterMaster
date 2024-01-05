import logging

import numpy as np
import pyqtgraph as pg
import scipy
from PyQt5 import QtCore

logging.basicConfig(
    level=logging.DEBUG,
    filename="log.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add an empty line to the log file
with open("log.log", "a") as log_file:
    log_file.write("\n")


# Global Variables
isPole = False
isZero = False
polePositions = []
zeroPositions = []
poleConjugates = []
zeroConjugates = []


##### Creating Zeros or Poles #####
###################################
def create(x, y):
    global isPole, isZero
    if isPole:
        logging.info(f"Adding Pole at Coordinates --> x:{x}, y:{y}")
        polePositions.append((x, y))
    elif isZero:
        logging.info(f"Adding Zero at Coordinates --> x:{x}, y:{y}")
        zeroPositions.append((x, y))


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


def handleUnitCircleClick(event, unitCirclePlot):
    global polePositions, zeroPositions
    if event.button() == QtCore.Qt.LeftButton:
        # Get the coordinates of the mouse click
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
        create(x, y)
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
