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
poles_conjugates_positions = []
zeros_conjugates_positions = []


# CREATING Zeros and Poles
def pole_mode():
    global is_pole, is_zero
    is_pole = True
    is_zero = False
    logging.info(f"isPole = {is_pole}")


def zero_mode():
    global is_pole, is_zero
    is_pole = False
    is_zero = True
    logging.info(f"isPole = {is_zero}")


def draw_item(unitCirclePlot, pos, symbol, color, items, positions_list):
    item = TargetItem(
        pos=pos,
        size=10,
        movable=True,
        symbol=symbol,
        pen=pg.mkPen(color),
    )
    unitCirclePlot.addItem(item)
    items.append(item)
    positions_list.append(pos)
    index = positions_list.index(pos)
    # Connect the sigPositionChanged signal to the update_positions function
    item.sigPositionChanged.connect(
        lambda: update_positions(item, positions_list, index)
    )


def handle_unit_circle_click(event, unitCirclePlot, addConjugatesCheckBox):
    global is_pole, is_zero
    global poles, zeros, poles_positions, zeros_positions
    global poles_conjugates, zeros_conjugates, poles_conjugates_positions, zeros_conjugates_positions
    if event.button() == QtCore.Qt.LeftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
        print(f"type: {type(pos)}")
        if is_pole:
            draw_item(unitCirclePlot, pos, "x", "r", poles, poles_positions)
        elif is_zero:
            draw_item(unitCirclePlot, pos, "o", "g", zeros, zeros_positions)


def update_positions(item, positions_list, index):
    # Update the position in the list when the item is moved
    new_pos = item.pos()
    print(f"new pos = {new_pos}")
    positions_list[index] = new_pos
    logging.debug(f"positions_List = {positions_list}")


# REMOVE All Zeros/Poles and RESET Design
def remove_poles(unitCirclePlot):
    global poles, poles_conjugates
    global poles_positions, poles_conjugates_positions

    remove(unitCirclePlot, poles + poles_conjugates)


def remove_zeros(unitCirclePlot):
    global zeros, zeros_conjugates
    global zeros_positions, zeros_conjugates_positions

    remove(unitCirclePlot, zeros + zeros_conjugates)


def reset_design(unitCirclePlot):
    global poles, poles_conjugates
    global poles_positions, poles_conjugates_positions
    global zeros, zeros_conjugates
    global zeros_positions, zeros_conjugates_positions

    remove(unitCirclePlot, poles + poles_conjugates)
    remove(unitCirclePlot, zeros + zeros_conjugates)


def remove(unitCirclePlot, whichList):
    for item in whichList:
        unitCirclePlot.removeItem(item)
