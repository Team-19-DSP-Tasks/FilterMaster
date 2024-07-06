import os

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QPushButton, QVBoxLayout
from scipy.signal import freqz, zpk2tf

save_directory = "Resources/All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)


class AllPassProcessButton(QPushButton):
    def __init__(self, allPassValue, index, parent=None):
        super(AllPassProcessButton, self).__init__(parent)

        self.allPassValue = allPassValue
        self.index = index

        # get the data you need
        (
            self.zero,
            self.pole,
            self.numerator,
            self.denominator,
        ) = self.Calculate_zero_and_pole()
        image_path = self.plot_response()

        # for appearance
        self.image_path = image_path
        self.name = f"a = {self.allPassValue}"

        # for calculating
        self.all_pass_frequencies_values = None
        self.all_pass_response_complex = None

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(QPixmap(image_path).scaled(75, 75, Qt.KeepAspectRatio))
        layout.addWidget(icon_label)

        text_label = QLabel(self.name)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        self.setFixedSize(100, 100)
        self.setCheckable(True)

    def Calculate_zero_and_pole(self):
        a_complex = complex(self.allPassValue)
        zeros = []
        poles = []
        pole = a_complex
        zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
        poles.append(pole)
        zeros.append(zero)

        numerator, denominator = zpk2tf(zeros, poles, 1)
        self.all_pass_frequencies_values, self.all_pass_response_complex = freqz(
            numerator, denominator, worN=8000
        )

        return zero, pole, numerator, denominator

    def plot_response(self):
        plt.figure()
        plt.plot(
            self.all_pass_frequencies_values,
            np.unwrap(np.angle(self.all_pass_response_complex)),
            color="orange",
            linewidth=5,
        )
        plt.axis("off")
        # Save the plot as a PNG file
        save_path = os.path.join(save_directory, f"phase_response_{self.index}.png")
        plt.savefig(save_path, transparent=True)
        plt.clf()
        return save_path

    def get_transfer_function(self):
        return self.numerator, self.denominator
