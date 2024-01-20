import csv

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImageReader
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class CSVLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText("\n\n Drop CSV File Here \n\n")
        self.setStyleSheet(
            """
            QLabel{
                border: 4px dashed #aaa
            }
        """
        )

    def set_csv_content(self, content):
        self.setText(content)


class CSVLabelArea(QWidget):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        mainLayout = QVBoxLayout()

        self.csvViewer = CSVLabel()
        mainLayout.addWidget(self.csvViewer)

        self.setLayout(mainLayout)

    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if (
            mime_data.hasUrls()
            and mime_data.urls()[0].isLocalFile()
            and QImageReader.supportedImageFormats().__contains__(
                mime_data.urls()[0].toString().split(".")[-1].encode()
            )
        ):
            event.acceptProposedAction()
        elif (
            mime_data.hasUrls()
            and mime_data.urls()[0].isLocalFile()
            and mime_data.urls()[0].toString().endswith(".csv")
        ):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime_data = event.mimeData()

        if mime_data.hasUrls() and mime_data.urls()[0].isLocalFile():
            file_path = mime_data.urls()[0].toLocalFile()

            if file_path.endswith(".csv"):
                self.process_csv(file_path)
                event.acceptProposedAction()

    def process_csv(self, file_path):
        with open(file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)

            # Ensure the CSV file is not empty
            try:
                first_column = [row[0] for row in csv_reader if row]
                print("First Column:", first_column)
                self.csvViewer.set_csv_content("\n".join(first_column))
            except IndexError:
                print("Error: The CSV file has empty rows or no data.")
