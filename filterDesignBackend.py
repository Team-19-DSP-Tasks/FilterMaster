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
# To store positions of poles and zeros
poles_positions = []
zeros_positions = []


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


def draw_item(pos, symbol, color, items):
    item = TargetItem(
        pos=pos,
        size=10,
        movable=True,
        symbol=symbol,
        pen=pg.mkPen(color),
    )
    items.append(item)


def handle_unit_circle_click(event, unitCirclePlot, addConjugatesCheckBox):
    global is_pole, is_zero, poles, zeros, poles_positions, zeros_positions, poles_conjugates, zeros_conjugates
    if event.button() == QtCore.Qt.leftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
        if is_pole:
            draw_item(pos, "x", "b", poles)
            poles_positions.append(pos)
        elif is_zero:
            draw_item(pos, "o", "g", zeros)
            zeros_positions.append(pos)


def update_positions(self):
    pass
