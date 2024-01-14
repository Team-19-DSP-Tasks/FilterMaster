# import matplotlib.pyplot as plt
# import numpy as np


# def phase_response(a, w):
#     H = (1 - a) / (1 - a * np.exp(-1j * w))
#     return np.angle(H)


# a = 1 / 5  # Replace with your desired value of 'a'
# w = np.linspace(-np.pi, np.pi, 1000)
# phase = phase_response(a, w)

# plt.plot(w, phase)
# plt.title("Phase Response of All-Pass Filter with a = " + str(a))
# plt.xlabel("Frequency (radians)")
# plt.ylabel("Phase (radians)")
# plt.show()

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import freqz


def allpass_filter_phase_response(a_coefficients, fs=1.0):
    # Calculate the frequency response using freqz
    _, phase_response = freqz(a=a_coefficients, worN=8000, fs=fs)

    # Convert phase response to degrees
    phase_response_deg = np.angle(phase_response, deg=True)

    return phase_response_deg


def plot_phase_response(phase_response, fs=1.0):
    # Frequency axis for plotting
    freq_axis = np.linspace(0, 0.5 * fs, len(phase_response))

    # Plot the phase response
    plt.figure(figsize=(10, 6))
    plt.plot(freq_axis, phase_response)
    plt.title("All-Pass Filter Phase Response")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Phase (degrees)")
    plt.grid(True)
    plt.show()


# Example usage
a_coefficients = [1, -0.5]  # Replace with your 'a' coefficients
sampling_frequency = 1000  # Replace with your desired sampling frequency

phase_response = allpass_filter_phase_response(a_coefficients, fs=sampling_frequency)
plot_phase_response(phase_response, fs=sampling_frequency)
