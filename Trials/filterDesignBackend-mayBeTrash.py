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
isDrag = False
what_item = ""  # what item i am close to.. to drag it with mouse
polePositions = []  # first added positions
zeroPositions = []  # first added positions
poleConjugates = []  # conjugates to the added positions
zeroConjugates = []  # conjugates to the added positions
poles = []  # combination of conjugates and the clicked positions
zeros = []  # combination of conjugates and the clicked positions

# Note: Manhattan Length = ∣x1 - x2| + |y1 - y2|


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
    # Get the coordinates of the mouse click
    pos = unitCirclePlot.mapToView(event.scenePos())
    x, y = pos.x(), pos.y()

    if event.button() == QtCore.Qt.LeftButton:
        if isDraggingMode(x, y, polePositions, "pole") or isDraggingMode(
            x, y, zeroPositions, "zero"
        ):
            print("I am Dragging")
            return
        elif not isDrag:
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


##### Dragging #####
####################
def initializeDragging(item):
    global isDrag, what_item
    isDrag = True
    what_item = item


def isDraggingMode(clickedX, clickedY, positions, item):
    global isDrag
    if not isDrag:
        Distancethreshold = 0.1
        for pos in positions:
            x = pos[0]
            y = pos[1]
            if (abs(x - clickedX) + abs(y - clickedY)) < Distancethreshold:
                initializeDragging(item)
                return True
    return False


def moveMouseForDragging(event, unitCirclePlot):
    global what_item
    if isDrag == False:
        return
    if isDrag:
        newPos = unitCirclePlot.plotItem.vb.mapSceneToView(event)
        if what_item == "pole":
            updatePositions(polePositions, newPos)
        if what_item == "zero":
            updatePositions(zeroPositions, newPos)


def updatePositions(positions, comparisonPos):
    Distancethreshold = 0.15
    for pos in positions:
        if (
            abs(pos[0] - comparisonPos.x()) + abs(pos[1] - comparisonPos.y())
        ) < Distancethreshold:
            print("kareem")
            # polePositions[i] = comparisonPos
            # drawConjugates()
