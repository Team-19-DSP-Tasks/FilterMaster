import logging

import pyqtgraph as pg
from PyQt5 import QtCore
from pyqtgraph import TargetItem

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

# Store the poles and zeros TargetItems for the ease of access
poles = []
zeros = []
conjPoles = []
conjZeros = []


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


def handleUnitCircleClick(event, unitCirclePlot, addConjugatesCheckBox):
    global polePositions, zeroPositions, poleConjugates, zeroPositions, poles, zeros, conjPoles, conjZeros
    # Get the coordinates of the mouse click
    if event.button() == QtCore.Qt.LeftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
        x, y = pos.x(), pos.y()
        # Add a symbol at the clicked position based on the current mode
        if isPole:
            symbol = "x"
            color = "b"
            polePositions.append((x, y))
            poleConjugates.append((x, -y))
        elif isZero:
            symbol = "o"
            color = "g"
            zeroPositions.append((x, y))
            zeroConjugates.append((x, -y))

        # Add the symbol to the unitCirclePlot
        symbol_item = TargetItem(
            pos=pos,
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        unitCirclePlot.addItem(symbol_item)

        if isPole:
            poles.append(symbol_item)
        elif isZero:
            zeros.append(symbol_item)

        # Call addConjugates if the checkbox is checked
        if addConjugatesCheckBox.isChecked():
            drawConjugates(
                unitCirclePlot,
                poleConjugates,
                symbol="x",
                color="r",
                conjugatesList=conjPoles,
            )
            drawConjugates(
                unitCirclePlot,
                zeroConjugates,
                symbol="o",
                color="y",
                conjugatesList=conjZeros,
            )
        # Log the click coordinates and add to the corresponding list
        logging.debug(f"poles: {polePositions}")
        logging.debug(f"zeros: {zeroPositions}")


##### Deleting Zeros or Poles or Both #####
###########################################
def removeSymbolsByType(unitCirclePlot, whichList):
    for item in whichList:
        unitCirclePlot.removeItem(item)


def removePoles(unitCirclePlot):
    global polePositions, poles, conjPoles, poleConjugates
    polePositions = []
    removeSymbolsByType(unitCirclePlot, poles)
    removeSymbolsByType(unitCirclePlot, conjPoles)
    poleConjugates = []


def removeZeros(unitCirclePlot):
    global zeroPositions, zeros, conjZeros, zeroConjugates
    zeroPositions = []
    removeSymbolsByType(unitCirclePlot, zeros)
    removeSymbolsByType(unitCirclePlot, conjZeros)
    zeroConjugates = []


def reset(unitCirclePlot):
    removePoles(unitCirclePlot)
    removeZeros(unitCirclePlot)


##### Add Conjugates #####
##########################
def drawConjugates(unitCirclePlot, conjugatesPositions, symbol, color, conjugatesList):
    for pos in conjugatesPositions:
        symbol_item = TargetItem(
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        symbol_item.setPos(pos)
        unitCirclePlot.addItem(symbol_item)
        conjugatesList.append(symbol_item)


def addConjugates(addConjugatesCheckBox, unitCirclePlot):
    global polePositions, zeroPositions, poleConjugates, zeroConjugates, conjPoles, conjZeros
    if addConjugatesCheckBox.isChecked():
        # Draw pole conjugates
        drawConjugates(unitCirclePlot, poleConjugates, "x", "r", conjPoles)

        # Draw zero conjugates
        drawConjugates(unitCirclePlot, zeroConjugates, "o", "y", conjZeros)

        logging.debug(f"polesConj: {poleConjugates}\nzerosConj: {zeroConjugates}")
