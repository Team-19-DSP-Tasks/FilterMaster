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
        self.poleConjugates = []
        self.zeroConjugates = []

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
        self.removeSymbolsByType(None)

    ##### Add Conjugates #####
    ##########################
    def drawConjugates(self, conjugates, symbol, color):
        for x, y in conjugates:
            symbol_item = pg.ScatterPlotItem(
                size=10,
                symbol=symbol,
                pen=pg.mkPen(None),
                brush=pg.mkBrush(color),
            )
            symbol_item.addPoints(x=[x], y=[y])
            self.ui.unitCirclePlot.addItem(symbol_item)

    def addConjugates(self):
        if self.ui.addConjugatesCheckBox.isChecked():
            # Create new lists for conjugates
            self.poleConjugates = [(x[0], -x[1]) for x in self.polePositions]
            self.zeroConjugates = [(x[0], -x[1]) for x in self.zeroPositions]

            # Draw pole conjugates
            self.drawConjugates(self.poleConjugates, "x", "r")

            # Draw zero conjugates
            self.drawConjugates(self.zeroConjugates, "o", "y")

            logging.debug(
                f"polesConj: {self.poleConjugates}\nzerosConj: {self.zeroConjugates}"
            )
        else:
            # Reset the lists if the checkbox is unchecked
            self.poleConjugates = []
            self.zeroConjugates = []

            # Remove existing conjugate symbols
            self.removeSymbolsByType("rx")
            self.removeSymbolsByType("oy")

            logging.debug(
                f"polesConj: {self.poleConjugates}\nzerosConj: {self.zeroConjugates}"
            )
