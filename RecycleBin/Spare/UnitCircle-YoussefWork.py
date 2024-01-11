import numpy as np
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QPointF

from PyQt6.QtGui import QColor
from functools import partial
import pyqtgraph as pg


class UnitCircle:
    def __init__(self, main_window):
        # Create lists to store poles and zeros
        self.main_window = main_window
        self.Poles = []
        self.Zeros = []
        self.zPlane = self.main_window.ui.zPlane
        self.zPlane.hideAxis('bottom')
        self.zPlane.hideAxis('left')
        self.zPlane.setLimits(xMin=-1.1, xMax=1.1, yMin=-1.1, yMax=1.1)
        self.zeros_button = self.main_window.ui.zerosButton
        self.poles_button = self.main_window.ui.polesButton
        self.zeros_button_pressed = True
        self.poles_button_pressed = False
        self.clicked_point = None  # for removing
        self.dragging_flag = False
        self.clear_mode = self.main_window.ui.Clear_selection.currentText()
        self.change_color()

        self.zeros_button.clicked.connect(self.handle_mode_of_insertion)
        self.poles_button.clicked.connect(self.handle_mode_of_insertion)
        self.main_window.Clear_selection.currentIndexChanged.connect(
            self.handle_clearing_mode)
        self.main_window.clear_button.clicked.connect(self.clear)

        # Set up the unit circle
        self.x, self.y = self.calculate_circle_points()
        self.update_plot(self.x, self.y)

        self.pole_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0), symbol="x")
        self.zero_symbol = pg.ScatterPlotItem(
            size=10, pen=pg.mkPen(None), brush=pg.mkBrush(0, 0, 255), symbol="o")
        self.zPlane.addItem(self.pole_symbol)
        self.zPlane.addItem(self.zero_symbol)

        self.pole_symbol.setData(pos=self.Poles)
        self.zero_symbol.setData(pos=self.Zeros)

        self.zPlane.scene().sigMouseClicked.connect(self.handleMouseClick)
        self.zPlane.scene().sigMouseClicked.connect(self.contextMenuEvent)
        self.zPlane.scene().sigMouseMoved.connect(self.handleMouseMove)

    def clear(self):
        if self.clear_mode == "Zeros":
            self.Zeros = list()
        elif self.clear_mode == "Poles":
            self.Poles = list()
        else:
            self.Poles = list()
            self.Zeros = list()
        self.zero_symbol.setData(pos=self.Zeros)
        self.pole_symbol.setData(pos=self.Poles)
        self.main_window.update_zeros_poles()
        self.main_window.plot_magnitude_and_phase()

    def handle_clearing_mode(self):
        self.clear_mode = self.main_window.ui.sender().currentText()

    def calculate_circle_points(self, num_points=100):
        theta = 2 * np.pi * np.linspace(0, 1, num_points)
        x = np.cos(theta)
        y = np.sin(theta)
        return x, y

    def handle_mode_of_insertion(self):
        source = self.main_window.ui.sender()
        if source is self.zeros_button:
            self.zeros_button_pressed = True
            self.poles_button_pressed = False
            self.change_color()
        elif source is self.poles_button:
            self.poles_button_pressed = True
            self.zeros_button_pressed = False
            self.change_color()

    def change_color(self):
        if self.zeros_button_pressed:
            zeros_color = QColor(
                255, 0, 0)
        else:
            zeros_color = QColor()
        self.zeros_button.setStyleSheet(
            f'background-color: {zeros_color.name()};')

        if self.poles_button_pressed:
            poles_color = QColor(
                255, 0, 0)
        else:
            poles_color = QColor()
        self.poles_button.setStyleSheet(
            f'background-color: {poles_color.name()};')

    def update_plot(self, x, y):
        self.zPlane.clear()
        self.zPlane.plot(x, y)
        vLine = pg.InfiniteLine(
            pos=0, angle=90, movable=False, pen=(255, 255, 255))
        hLine = pg.InfiniteLine(
            pos=0, angle=0, movable=False, pen=(255, 255, 255))
        self.zPlane.addItem(vLine)
        self.zPlane.addItem(hLine)

    def add_pole(self, pos):
        self.Poles.append(pos)
        self.pole_symbol.setData(pos=self.Poles)

    def add_zero(self, pos):
        self.Zeros.append(pos)
        self.zero_symbol.setData(pos=self.Zeros)

    def remove_point(self, item, pos):
        if item == 'pole':
            self.Poles.remove(pos)
            self.pole_symbol.setData(pos=self.Poles)
        elif item == 'zero':
            self.Zeros.remove(pos)
            self.zero_symbol.setData(pos=self.Zeros)

    def handleMouseClick(self, event):
        # Handle mouse clicks to add, remove, or move poles/zeros
        if self.poles_button_pressed or self.zeros_button_pressed:
            pos = self.zPlane.plotItem.vb.mapSceneToView(event.scenePos())
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if self.check_for_dragging(pos):
                    print("activate dragging")
                    return
                elif self.dragging_flag == False:
                    print("adding")

                    if self.poles_button_pressed:
                        if self.main_window.Conj_pair.isChecked():
                            self.add_pole(pos)
                            conjugate_pos = QPointF(pos.x(), -pos.y())
                            self.add_pole(conjugate_pos)
                        else:
                            self.add_pole(pos)

                    if self.zeros_button_pressed:
                        if self.main_window.Conj_pair.isChecked():
                            self.add_zero(pos)
                            conjugate_pos = QPointF(pos.x(), -pos.y())
                            self.add_zero(conjugate_pos)
                        else:
                            self.add_zero(pos)
                else:
                    print("deactivate dragging")
                    self.dragging_flag = False

            elif event.button() == QtCore.Qt.MouseButton.RightButton:
                self.clicked_point = pos
        self.main_window.update_zeros_poles()
        self.main_window.plot_magnitude_and_phase()

    def check_for_dragging(self, pos):
        if self.dragging_flag == False:
            threshold = 0.1  # adjustable
            for pole_pos in self.Poles:
                if (pole_pos - pos).manhattanLength() < threshold:
                    self.start_dragging(pos, 'pole', pole_pos)
                    return True
            for zero_pos in self.Zeros:
                if (zero_pos - pos).manhattanLength() < threshold:
                    self.start_dragging(pos, 'zero', zero_pos)
                    return True
        return False

    def start_dragging(self, start_pos, item, original_pos):
        self.dragging_flag = True
        self.dragging_item = item

    def handleMouseMove(self, event):
        if self.dragging_flag == False:
            return
        if self.dragging_flag:
            new_pos = self.zPlane.plotItem.vb.mapSceneToView(
                event)
            threshold = 0.15  # Adjustable
            if self.dragging_item == 'pole':
                for i, pole_pos in enumerate(self.Poles):
                    if (pole_pos - new_pos).manhattanLength() < threshold:
                        self.Poles[i] = new_pos
                        self.pole_symbol.setData(pos=self.Poles)
                        break
            elif self.dragging_item == 'zero':
                for i, zero_pos in enumerate(self.Zeros):
                    if (zero_pos - new_pos).manhattanLength() < threshold:
                        self.Zeros[i] = QPointF(new_pos)
                        self.zero_symbol.setData(pos=self.Zeros)
                        break
        self.main_window.update_zeros_poles()
        self.main_window.plot_magnitude_and_phase()

    def contextMenuEvent(self, event):
        if self.clicked_point is not None:
            menu = QtWidgets.QMenu()
            threshold = 0.1
            clicked_point = self.clicked_point

            for pole_pos in self.Poles:
                if (pole_pos - clicked_point).manhattanLength() < threshold:
                    action = menu.addAction('Remove Pole')
                    action.triggered.connect(
                        partial(self.remove_point, 'pole', pole_pos))
                    self.zPlane.setMenuEnabled(False)

            for zero_pos in self.Zeros:
                if (zero_pos - clicked_point).manhattanLength() < threshold:
                    action = menu.addAction('Remove Zero')
                    action.triggered.connect(
                        partial(self.remove_point, 'zero', zero_pos))
                    self.zPlane.setMenuEnabled(False)

            global_pos = self.zPlane.mapToGlobal(
                self.zPlane.mapFromScene(event.scenePos()))
            action = menu.exec(global_pos)

            if action:
                # If an action was triggered, reset clicked point
                self.clicked_point = None
                self.zPlane.setMenuEnabled(True)
                self.main_window.update_zeros_poles()
                self.main_window.plot_magnitude_and_phase()
