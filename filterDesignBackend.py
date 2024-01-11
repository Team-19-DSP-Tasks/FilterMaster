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


def zero_mode():
    global is_pole, is_zero
    is_pole = False
    is_zero = True


def draw_item(
    unitCirclePlot, pos, symbol, color, items, positions_list, conjugates_list
):
    global poles_conjugates_positions, zeros_conjugates_positions
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
    conjugates_list.append(pg.Point(pos.x(), -pos.y()))  # Add the conjugate position
    if is_pole:
        poles_conjugates_positions.append(pg.Point(pos.x(), -pos.y()))
    elif is_zero:
        zeros_conjugates_positions.append(pg.Point(pos.x(), -pos.y()))
    index = positions_list.index(pos)
    # Connect the sigPositionChanged signal to the update_positions function
    item.sigPositionChanged.connect(lambda: update_positions(item, index))


def handle_unit_circle_click(event, unitCirclePlot, addConjugatesCheckBox):
    global is_pole, is_zero
    global poles, zeros, poles_positions, zeros_positions
    global poles_conjugates, zeros_conjugates, poles_conjugates_positions, zeros_conjugates_positions
    if event.button() == QtCore.Qt.LeftButton:
        pos = unitCirclePlot.mapToView(event.scenePos())
        if is_pole:
            draw_item(
                unitCirclePlot,
                pos,
                "x",
                "r",
                poles,
                poles_positions,
                poles_conjugates_positions,
            )
        elif is_zero:
            draw_item(
                unitCirclePlot,
                pos,
                "o",
                "g",
                zeros,
                zeros_positions,
                zeros_conjugates_positions,
            )

        if addConjugatesCheckBox.isChecked():
            if is_pole:
                draw_conjugates(
                    unitCirclePlot, [poles_conjugates_positions[-1]], "x", "b"
                )
            elif is_zero:
                draw_conjugates(
                    unitCirclePlot, [zeros_conjugates_positions[-1]], "o", "y"
                )


def update_positions(item, index):
    global poles_positions, zeros_positions
    global poles_conjugates_positions, zeros_conjugates_positions
    # Update the position in the list when the item is moved
    new_pos = item.pos()
    if item in poles:
        poles_positions[index] = new_pos
        poles_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())
    elif item in zeros:
        zeros_positions[index] = new_pos
        zeros_conjugates_positions[index] = pg.Point(new_pos.x(), -new_pos.y())


# REMOVE All Zeros/Poles and RESET Design
def remove_poles(unitCirclePlot):
    global poles, poles_conjugates
    global poles_positions, poles_conjugates_positions
    remove(unitCirclePlot, poles + poles_conjugates)
    # Empty all pole related lists
    poles.clear()
    poles_positions.clear()
    poles_conjugates.clear()
    poles_conjugates_positions.clear()


def remove_zeros(unitCirclePlot):
    global zeros, zeros_conjugates
    global zeros_positions, zeros_conjugates_positions
    remove(unitCirclePlot, zeros + zeros_conjugates)
    # Empty all zero related lists
    zeros.clear()
    zeros_positions.clear()
    zeros_conjugates.clear()
    zeros_conjugates_positions.clear()


def reset_design(unitCirclePlot):
    global poles, poles_conjugates
    global poles_positions, poles_conjugates_positions
    global zeros, zeros_conjugates
    global zeros_positions, zeros_conjugates_positions
    remove(unitCirclePlot, poles + poles_conjugates + zeros + zeros_conjugates)
    # Empty all lists
    poles.clear()
    poles_positions.clear()
    poles_conjugates.clear()
    poles_conjugates_positions.clear()
    zeros.clear()
    zeros_positions.clear()
    zeros_conjugates.clear()
    zeros_conjugates_positions.clear()


def remove(unitCirclePlot, whichList):
    for item in whichList:
        unitCirclePlot.removeItem(item)


# HANDLING CONJUGATES
def draw_conjugates(unitCirclePlot, conjugates_positions, symbol, color):
    global poles_conjugates, zeros_conjugates
    for pos in conjugates_positions:
        item = TargetItem(
            size=10,
            movable=True,
            symbol=symbol,
            pen=pg.mkPen(color),
        )
        item.setPos(pos)
        unitCirclePlot.addItem(item)
        if symbol == "x":
            poles_conjugates.append(item)
        elif symbol == "o":
            zeros_conjugates.append(item)


def handle_conjugates(addConjugatesCheckBox, unitCirclePlot):
    global poles_conjugates, zeros_conjugates
    global poles_conjugates_positions, zeros_conjugates_positions
    if addConjugatesCheckBox.isChecked():
        draw_conjugates(unitCirclePlot, poles_conjugates_positions, "x", "b")
        draw_conjugates(unitCirclePlot, zeros_conjugates_positions, "o", "y")
    else:
        remove(unitCirclePlot, poles_conjugates + zeros_conjugates)
        poles_conjugates.clear()
        zeros_conjugates.clear()
