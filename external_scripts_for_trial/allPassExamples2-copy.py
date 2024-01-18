import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import os

def plot_phase_response(a_values, save_directory):
    os.makedirs(save_directory, exist_ok=True)

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
        plt.plot(w, np.unwrap(np.angle(h)), color="orange", linewidth=5)
        plt.axis("off")
        
        # Save the plot as a PNG file
        save_path = os.path.join(save_directory, f"phase_response_{idx}.png")
        plt.savefig(save_path, transparent=True)
        plt.clf()

    # Cascade the filters
    b_cascade, a_cascade = 1, 1
    for a_value in a_values:
        a_complex = complex(a_value)
        zeros = [(1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))]
        poles = [a_complex]
        b, a = signal.zpk2tf(zeros, poles, 1)
        b_cascade, a_cascade = signal.convolve(b_cascade, b), signal.convolve(a_cascade, a)

    # Calculate the frequency response of the cascaded filter
    w_cascade, h_cascade = signal.freqz(b_cascade, a_cascade, worN=8000)

    # Plot the phase response of the cascaded filter
    plt.figure()
    plt.plot(w_cascade, np.unwrap(np.angle(h_cascade)), color="orange", linewidth=5)
    plt.title('Cascaded Filter Phase Response')
    plt.xlabel('Frequency')
    plt.ylabel('Phase')
    plt.grid(True)
    plt.show()

    # Plot zeros and poles of the cascaded filter
    plt.figure()
    plt.scatter(np.real(zeros), np.imag(zeros), marker='o', label='Zeros', color='blue')
    plt.scatter(np.real(poles), np.imag(poles), marker='x', label='Poles', color='red')
    plt.title('Zeros and Poles of Cascaded Filter')
    plt.xlabel('Real')
    plt.ylabel('Imaginary')
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    plt.grid(color = 'gray', linestyle = '--', linewidth = 0.5)
    plt.legend()
    plt.show()

# List of 'a' values
a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2, 3, 0.2]

# Create a directory to save the plots
save_directory = "All-Pass-Phase-Responses"

# Call the function to plot individual and cascaded phase responses, and zeros/poles
plot_phase_response(a_values, save_directory)
