from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QValidator


class CustomValidator(QValidator):
    def __init__(self, parent=None):
        super(CustomValidator, self).__init__(parent)
        self.regex = QRegExp("[0-9j+-.]+")

    def validate(self, input_str, pos):
        if pos == 0 and input_str == "":
            # Allow deleting the first character
            return QValidator.Acceptable, input_str, pos

        if self.regex.exactMatch(input_str):
            return QValidator.Acceptable, input_str, pos
        else:
            return QValidator.Invalid, input_str, pos
