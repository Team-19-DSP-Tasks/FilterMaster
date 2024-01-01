import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# Define zeros and poles
zeros = [0.5 + 0.5j, 0.5 - 0.5j]  # Example zeros
poles = [0.2 + 0.3j, 0.2 - 0.3j]  # Example poles

# Create the transfer function
sys = signal.ZerosPolesGain(zeros, poles, 1)

# Frequency response
w, h = signal.freqresp(sys)

# Plot the magnitude and phase response
plt.figure(figsize=(10, 6))

plt.subplot(2, 1, 1)
plt.plot(w, np.abs(h))
plt.title("Filter Magnitude Response")
plt.xlabel("Frequency [radians / second]")
plt.ylabel("Magnitude")

plt.subplot(2, 1, 2)
plt.plot(w, np.angle(h))
plt.title("Filter Phase Response")
plt.xlabel("Frequency [radians / second]")
plt.ylabel("Phase [radians]")

plt.tight_layout()
plt.show()
