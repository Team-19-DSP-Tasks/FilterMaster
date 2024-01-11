import logging

import pyqtgraph as pg
from PyQt5 import QtCore
from pyqtgraph import TargetItem

logging.basicConfig(
    level=logging.DEBUG,
    filename="filterDesignBackend.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Add an empty line to the log file
with open("filterDesignBackend.log", "a") as log_file:
    log_file.write("\n")

# Global Variables
# To control poles and zeros creation
is_pole = False
is_zero = False
# To store poles and zeros TargetItems
poles = []
zeros = []
poles_conjugates = []
zeros_conjugates = []


# Creating Zeros and Poles
def pole_mode():
    global is_pole, is_zero
    is_pole = True
    is_zero = False
    logging.info(f"isPole = {is_pole}")
    pass


def zero_mode():
    global is_pole, is_zero
    is_pole = False
    is_zero = True
    logging.info(f"isPole = {is_zero}")
    pass


def handleUnitCircleClick(event, unitCirclePlot, addConjugatesCheckBox):
    if event.button() == QtCore.Qt.leftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
