import matplotlib.pyplot as plt
from scipy import signal

a_values = [0.7, 1 + 2j, 0.3 + 0.2j, 1.5j, 5 + 1j, -0.9, 1.2]

for i, a in enumerate(a_values):
    sys = signal.TransferFunction([1, -a], [1, a])
    w, phase, _ = sys.bode()
    plt.semilogx(w, phase, color="orange", linewidth=3.5)
    # plt.title(f"Phase response of all-pass filter with a={a}")
    # plt.xlabel("Frequency (rad/s)")
    # plt.ylabel("Phase (deg)")
    plt.axis("off")
    plt.gca().set_facecolor("orange")
    plt.savefig(f"phase_response_{i}.png", transparent=True)
    plt.clf()
