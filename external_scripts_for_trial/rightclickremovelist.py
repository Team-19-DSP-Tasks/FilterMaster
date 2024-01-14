import sys

from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QListWidget,
    QMenu,
    QVBoxLayout,
    QWidget,
)


class ListWidgetWithContextMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(["Item 1", "Item 2", "Item 3", "Item 4"])

        # Set up the context menu
        self.context_menu = QMenu(self)
        remove_action = QAction("Remove", self)
        remove_action.triggered.connect(self.removeSelectedItem)
        self.context_menu.addAction(remove_action)

        # Connect the context menu to the list widget
        self.list_widget.setContextMenuPolicy(
            3
        )  # Set context menu policy to CustomContextMenu
        self.list_widget.customContextMenuRequested.connect(self.showContextMenu)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)

        self.setGeometry(100, 100, 300, 200)
        self.setWindowTitle("List Widget with Context Menu")
        self.show()

    def showContextMenu(self, pos):
        # Show the context menu at the specified position
        self.context_menu.exec_(self.list_widget.mapToGlobal(pos))

    def removeSelectedItem(self):
        # Remove the selected item from the list widget
        selected_item = self.list_widget.currentItem()
        if selected_item is not None:
            self.list_widget.takeItem(self.list_widget.row(selected_item))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ListWidgetWithContextMenu()
    sys.exit(app.exec_())
