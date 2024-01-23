# # Import the scipy.signal module
# import scipy.signal as sig

# # Define the zeros and poles of the filter
# z = [0.5, -0.5]  # Zeros
# p = [0.9, -0.9]  # Poles

# # Convert the zeros and poles to numerator and denominator of the transfer function
# num, den = sig.zpk2tf(
#     z, p, 1
# )  # The third argument is the gain, which is 1 in this case

# # Initialize the input and output signals
# x = [1, 2, 3, 4, 5]  # Your data
# y = [0] * len(x)  # Output signal

# # Loop over the data samples
# for n in range(len(x)):
#     # Compute the output sample using the difference equation
#     y[n] = sum(num * x[n - len(num) + 1 : n + 1][::-1]) - sum(
#         den[1:] * y[n - len(den) + 2 : n + 1][::-1]
#     )
#     # The slicing and reversing operations are used to get the correct values of x and y

# # Return the output signal
# print(y)

# Import the scipy.signal module
import scipy.signal as sig

# Define the zeros and poles of the filter
z = [0.5, -0.5]  # Zeros
p = [0.9, -0.9]  # Poles

# Convert the zeros and poles to numerator and denominator of the transfer function
num, den = sig.zpk2tf(
    z, p, 1
)  # The third argument is the gain, which is 1 in this case

# Initialize the input and output signals
x = [0] * len(num) + [1, 2, 3, 4, 5]  # Your data, padded with zeros
y = [0] * len(x)  # Output signal

# Loop over the data samples
for n in range(len(num), len(x)):
    # Compute the output sample using the difference equation
    y[n] = sum(num * x[n - len(num) + 1 : n + 1][::-1]) - sum(
        den[1:] * y[n - len(den) + 2 : n + 1][::-1]
    )
    # The slicing and reversing operations are used to get the correct values of x and y

# Return the output signal
print(y)
