# import matplotlib.pyplot as plt
# import numpy as np
# from scipy import signal

# # List of 'a' values
# a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2, 3, 0.2]

# # Create a directory to save the plots
# import os

# save_directory = "All-Pass-Phase-Responses"
# os.makedirs(save_directory, exist_ok=True)

# # Initialize variables to store cascaded transfer function
# numerator_cascade = [1]
# denominator_cascade = [1]

# # Iterate over 'a' values
# for idx, a_value in enumerate(a_values):
#     a_complex = complex(a_value)
#     zeros = []
#     poles = []
#     poles.append(a_complex)
#     zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
#     zeros.append(zero)

#     # Calculate frequency response using freqz
#     b, a = signal.zpk2tf(zeros, poles, 1)
#     w, h = signal.freqz(b, a, worN=8000)

#     # Cascade the transfer functions
#     numerator_cascade = np.convolve(numerator_cascade, b)
#     denominator_cascade = np.convolve(denominator_cascade, a)

#     # Plot the phase response
#     plt.plot(w, np.unwrap(np.angle(h)), color="orange", linewidth=5)

# # Calculate the final phase response using the cascaded transfer function
# w_cascade, h_cascade = signal.freqz(numerator_cascade, denominator_cascade, worN=8000)

# # Plot the final phase response
# plt.figure()
# plt.plot(w_cascade, np.unwrap(np.angle(h_cascade)), color="orange", linewidth=5)
# plt.xlabel('Frequency [radians/sample]')
# plt.ylabel('Phase [radians]')
# plt.title('Cascaded All-Pass Filters Phase Response')
# plt.show()

# import matplotlib.pyplot as plt
# import numpy as np
# from scipy import signal

# # List of 'a' values
# a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2, 3, 0.2]

# # Create a directory to save the plots
# import os

# save_directory = "All-Pass-Phase-Responses"
# os.makedirs(save_directory, exist_ok=True)

# # Initialize lists of tuples for zeros and poles
# zeros_coords = []
# poles_coords = []

# # Iterate over 'a' values
# for idx, a_value in enumerate(a_values):
#     a_complex = complex(a_value)
#     zeros = []
#     poles = []
#     pole = a_complex
#     poles.append(pole)
#     zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
#     zeros.append(zero)

#     # Append (x, y) coordinates to the lists
#     zeros_coords.append((zero.real, zero.imag))
#     poles_coords.append((pole.real, pole.imag))

#     # Calculate frequency response using freqz
#     b, a = signal.zpk2tf(zeros, poles, 1)
#     w, h = signal.freqz(b, a, worN=8000)

# # Plot zeros and poles
# zeros_x, zeros_y = zip(*zeros_coords)
# poles_x, poles_y = zip(*poles_coords)

# plt.scatter(zeros_x, zeros_y, marker="o", label="Zeros")
# plt.scatter(poles_x, poles_y, marker="x", label="Poles")

# # Plot settings
# plt.xlabel("Real")
# plt.ylabel("Imaginary")
# plt.title("Zeros and Poles")
# plt.legend()
# plt.grid(True)
# plt.show()

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# List of 'a' values
a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2, 3, 0.2]

# Create a directory to save the plots
import os

save_directory = "All-Pass-Phase-Responses"
os.makedirs(save_directory, exist_ok=True)

# Initialize lists of tuples for zeros and poles
zeros_coords = []
poles_coords = []

# Iterate over 'a' values
for idx, a_value in enumerate(a_values):
    a_complex = complex(a_value)
    zeros = []
    poles = []
    pole = a_complex
    poles.append(pole)
    zero = (1 / np.abs(a_complex)) * np.exp(1j * np.angle(a_complex))
    zeros.append(zero)

    # Append (x, y) coordinates to the lists
    zeros_coords.append((zero.real, zero.imag))
    poles_coords.append((pole.real, pole.imag))

    # Calculate frequency response using freqz
    b, a = signal.zpk2tf(zeros, poles, 1)
    w, h = signal.freqz(b, a, worN=8000)

# Find the maximum x and y values
max_zeros_x = max(zeros_coords, key=lambda x: x[0])[0]
max_zeros_y = max(zeros_coords, key=lambda x: x[1])[1]
max_poles_x = max(poles_coords, key=lambda x: x[0])[0]
max_poles_y = max(poles_coords, key=lambda x: x[1])[1]

# Print the maximum x and y values
print("Maximum Zeros X:", max_zeros_x)
print("Maximum Zeros Y:", max_zeros_y)
print("Maximum Poles X:", max_poles_x)
print("Maximum Poles Y:", max_poles_y)

# Plot zeros and poles
zeros_x, zeros_y = zip(*zeros_coords)
poles_x, poles_y = zip(*poles_coords)

plt.scatter(zeros_x, zeros_y, marker="o", label="Zeros")
plt.scatter(poles_x, poles_y, marker="x", label="Poles")

# Plot settings
plt.xlabel("Real")
plt.ylabel("Imaginary")
plt.title("Zeros and Poles")
plt.legend()
plt.grid(True)
plt.show()
