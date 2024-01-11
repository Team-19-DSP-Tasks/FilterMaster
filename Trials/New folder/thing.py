import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# Replace these lists with your x and y coordinates for poles and zeros
zeros_x = [0.37683741648106905, -0.09888641425389744, 0.4035634743875278]
zeros_y = [
    -0.1506976744186046,
    -0.11720930232558135,
    0.41860465116279066,
]

poles_x = [0.18975501113585747, -0.42494432071269483]
poles_y = [0.5413953488372093, 0.41860465116279066]


# Combine x and y coordinates into complex numbers
zeros = np.array(zeros_x) + 1j * np.array(zeros_y)
poles = np.array(poles_x) + 1j * np.array(poles_y)

# Create a transfer function using the zeros and poles
sys = signal.TransferFunction(np.poly(zeros), np.poly(poles))

# Frequency range for the frequency response plot
w, mag, phase = signal.bode(sys)

# Plot magnitude response
plt.figure()
plt.subplot(2, 1, 1)
plt.semilogx(w, mag)
plt.title("Magnitude Response")
plt.xlabel("Frequency [rad/s]")
plt.ylabel("Magnitude [dB]")

# Plot phase response
plt.subplot(2, 1, 2)
plt.semilogx(w, phase)
plt.title("Phase Response")
plt.xlabel("Frequency [rad/s]")
plt.ylabel("Phase [degrees]")

plt.tight_layout()
plt.show()
