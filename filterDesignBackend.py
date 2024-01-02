import logging

import pyqtgraph as pg
from PyQt5 import QtCore

logging.basicConfig(
    level=logging.DEBUG,
    filename="log.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add an empty line to the log file
with open("log.log", "a") as log_file:
    log_file.write("\n")


class ZPlane:
    def __init__(self, ui):
        self.ui = ui

        # variables of the class
        self.isPole = False
        self.isZero = False
        self.polePositions = []
        self.zeroPositions = []

        # UI Objects Connections
        self.ui.addZero.clicked.connect(self.create_zero)
        self.ui.addPole.clicked.connect(self.create_pole)
        self.ui.removeAllPoles.clicked.connect(self.removePoles)
        self.ui.removeAllZeros.clicked.connect(self.removeZeros)
        self.ui.resetDesign.clicked.connect(self.reset)
        self.ui.addConjugatesCheckBox.stateChanged.connect(self.addConjugates)
        # Connect the mouseClickEvent signal to the handleUnitCircleClick method
        self.ui.unitCirclePlot.scene().sigMouseClicked.connect(
            self.handleUnitCircleClick
        )

    ##### Creating Zeros or Poles #####
    ###################################
    def create(self, x, y):
        if self.isPole:
            logging.info(f"Adding Pole at Coordinates --> x:{x}, y:{y}")
            self.polePositions.append((x, y))
        elif self.isZero:
            logging.info(f"Adding Zero at Coordinates --> x:{x}, y:{y}")
            self.zeroPositions.append((x, y))

    def create_pole(self):
        self.isPole = True
        logging.info(f"isPole = {self.isPole}")
        self.isZero = False

    def create_zero(self):
        self.isZero = True
        logging.info(f"isZero = {self.isZero}")
        self.isPole = False

    def handleUnitCircleClick(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Get the coordinates of the mouse click
            pos = self.ui.unitCirclePlot.mapToView(event.scenePos())
            x, y = pos.x(), pos.y()

            # Add a symbol at the clicked position based on the current mode
            if self.isPole:
                symbol = "x"
                color = "b"
            elif self.isZero:
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
            self.ui.unitCirclePlot.addItem(symbol_item)

            # Log the click coordinates and add to the corresponding list
            self.create(x, y)
            logging.debug(f"poles: {self.polePositions}")
            logging.debug(f"zeros: {self.zeroPositions}")

    ##### Deleting Zeros or Poles or Both #####
    ###########################################
    def removeSymbolsByType(self, symbolType=None):
        # Remove symbols of the specified type or all symbols if type is None
        for item in self.ui.unitCirclePlot.items():
            if isinstance(item, pg.ScatterPlotItem) and (
                symbolType is None or item.opts["symbol"] == symbolType
            ):
                self.ui.unitCirclePlot.removeItem(item)

        # Reset the corresponding positions list if a specific type is provided
        if symbolType == "x":
            self.polePositions = []
        elif symbolType == "o":
            self.zeroPositions = []
        else:
            self.polePositions = []
            self.zeroPositions = []

    def removePoles(self):
        self.removeSymbolsByType("x")

    def removeZeros(self):
        self.removeSymbolsByType("o")

    def reset(self):
        # Remove all symbols from the graph
        self.removeSymbolsByType(None)

    ##### Add Conjugates #####
    ##########################
    def copyCoordinates(self, coordinatesList):
        new_CoordinatesList = [(x[0], -x[1]) for x in coordinatesList]
        coordinatesList += new_CoordinatesList

    def addConjugates(self):
        if self.ui.addConjugatesCheckBox.isChecked():
            self.copyCoordinates(self.polePositions)
            self.copyCoordinates(self.zeroPositions)
            logging.debug(f"poles: {self.polePositions}\nzeros: {self.zeroPositions}")
