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
    def __init__(self, name, image_path, parent=None):
        super(ProcessButton, self).__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QPixmap(image_path).scaled(50, 50, Qt.KeepAspectRatio))
        layout.addWidget(icon_label)

        text_label = QLabel(name)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        self.setFixedSize(100, 100)
        self.setCheckable(True)

        # Connect click event to add the widget to the workspace
        # self.clicked.connect(self.add_to_workspace)

    # def add_to_workspace(self):
    #     workspace.add_process(self)


class Workspace(QGraphicsView):
    def __init__(self, parent=None):
        super(Workspace, self).__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

    def add_process(self, process_button):
        # Create a new instance of the process button in the workspace
        proxy_widget = QGraphicsProxyWidget()
        proxy_widget.setWidget(process_button)
        self.scene.addItem(proxy_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.central_widget = Workspace(self)
        self.setCentralWidget(self.central_widget)

        # Add process buttons to a side panel
        self.process1 = ProcessButton("Monitor", "monitor.png", self)
        self.process2 = ProcessButton("Keyboard", "keyboard.png", self)

        # Adjust positions as needed
        self.process1.setGeometry(10, 10, 100, 100)
        self.process2.setGeometry(10, 120, 100, 100)

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
