import sys

from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ScrollAreaExample(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Create the main layout
        main_layout = QVBoxLayout(self)

        # Create the first scroll area
        self.scroll_area1 = QScrollArea(self)
        self.scroll_area1.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area1)

        # Create a widget to contain the buttons for the first scroll area
        self.widget1 = QWidget()
        self.scroll_area1.setWidget(self.widget1)

        # Create a grid layout for the buttons in the first scroll area
        self.layout1 = QGridLayout(self.widget1)
        self.populate_buttons()

        # Create the second scroll area
        self.scroll_area2 = QScrollArea(self)
        self.scroll_area2.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area2)

        # Create a widget to contain the buttons for the second scroll area
        self.widget2 = QWidget()
        self.scroll_area2.setWidget(self.widget2)

        # Create a grid layout for the buttons in the second scroll area
        self.layout2 = QGridLayout(self.widget2)

        # Set the main layout for the widget
        self.setLayout(main_layout)

        # Show the GUI
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Scroll Area Example")
        self.show()

    def populate_buttons(self):
        # Create and add buttons to the first scroll area layout
        for i in range(10):
            button = QPushButton(f"Button {i}")
            button.clicked.connect(
                lambda _, btn=button: self.on_button_clicked(
                    btn, self.layout1, self.layout2
                )
            )
            self.layout1.addWidget(button, i // 3, i % 3)

    def on_button_clicked(self, button, source_layout, target_layout):
        # Remove the button from the source layout
        source_layout.removeWidget(button)

        # Add the button to the target layout
        target_layout.addWidget(button)

        # Adjust the scroll bar positions
        self.scroll_area1.verticalScrollBar().setValue(
            self.scroll_area1.verticalScrollBar().maximum()
        )
        self.scroll_area2.verticalScrollBar().setValue(
            self.scroll_area2.verticalScrollBar().maximum()
        )


def main():
    app = QApplication(sys.argv)
    ex = ScrollAreaExample()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
