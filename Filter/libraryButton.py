import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsProxyWidget,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)


class ProcessButton(QPushButton):
    def __init__(self, name, image_path, allPassValue, parent=None):
        super(ProcessButton, self).__init__(parent)

        self.allPassValue = allPassValue

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QPixmap(image_path).scaled(75, 75, Qt.KeepAspectRatio))
        layout.addWidget(icon_label)

        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        self.setFixedSize(100, 100)
        self.setCheckable(True)
