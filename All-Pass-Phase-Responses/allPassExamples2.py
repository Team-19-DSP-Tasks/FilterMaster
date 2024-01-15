import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# List of 'a' values
a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2, 3, 0.2]

# Create a directory to save the plots
import os

save_directory = "All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)

# Iterate over 'a' values
for idx, a_value in enumerate(a_values):
    a_complex = complex(a_value)
    zeros = []
    poles = []
    poles.append(a_complex)
    zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
    zeros.append(zero)

    # Calculate frequency response using freqz
    b, a = signal.zpk2tf(zeros, poles, 1)
    w, h = signal.freqz(b, a, worN=8000)

    # Plot the phase response
    plt.figure()
    plt.plot(w, np.angle(h), color="orange", linewidth=5)
    plt.axis("off")
    # Save the plot as a PNG file
    save_path = os.path.join(save_directory, f"phase_response_{idx}.png")
    plt.savefig(save_path, transparent=True)
    plt.clf()
