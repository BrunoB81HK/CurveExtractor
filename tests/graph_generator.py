import matplotlib.pyplot as plt
from typing import Tuple
import numpy.random
import numpy as np


# Global parameters
STYLE = "fivethirtyeight"
PLACEHOLDER_RUN = True
KNOWN_XLIN_YLIN_RUN = True
KNOWN_XLOG_YLIN_RUN = True
KNOWN_XLIN_YLOG_RUN = True
KNOWN_XLOG_YLOG_RUN = True

# Placeholder parameters
PLACEHOLDER_FILENAME = "./placeholder.png"
PLACEHOLDER_TITLE = "CurveFinder"
PLACEHOLDER_XLABEL = "Time t [s]"
PLACEHOLDER_YLABEL = r"Temperature T [$\degree$]"
PLACEHOLDER_NUM_CURVE = 2
PLACEHOLDER_SEED = 1851895
PLACEHOLDER_RANDOM_SEED = False

# Known x lin y lin parameters
KNOWN_XLIN_YLIN_FILENAME = "./known_lin_lin.png"
KNOWN_XLIN_YLIN_COEFFS = (3, -10, 10, -2, 0)
KNOWN_XLIN_YLIN_XLABEL = "Time t [s]"
KNOWN_XLIN_YLIN_YLABEL = r"Temperature T [$\degree$]"

# Known x log y lin parameters
KNOWN_XLOG_YLIN_FILENAME = "./known_log_lin.png"
KNOWN_XLOG_YLIN_COEFFS = (0, -0.3, 1.5, -1, 0)
KNOWN_XLOG_YLIN_XLABEL = "Time t [s]"
KNOWN_XLOG_YLIN_YLABEL = r"Temperature T [$\degree$]"

# Known x lin y log parameters
KNOWN_XLIN_YLOG_FILENAME = "./known_lin_log.png"
KNOWN_XLIN_YLOG_COEFFS = (3, -10, 10, -2, 0)
KNOWN_XLIN_YLOG_XLABEL = "Time t [s]"
KNOWN_XLIN_YLOG_YLABEL = r"Temperature T [$\degree$]"

# Known x log y log parameters
KNOWN_XLOG_YLOG_FILENAME = "./known_log_log.png"
KNOWN_XLOG_YLOG_COEFFS = (0.8, -6, 10, 10, 0)
KNOWN_XLOG_YLOG_XLABEL = "Time t [s]"
KNOWN_XLOG_YLOG_YLABEL = r"Temperature T [$\degree$]"


# Useful functions
def coeffs_to_title(coeffs: Tuple[float, ...]) -> str:
    equation = ""
    order = len(coeffs) - 1
    for c, o in zip(coeffs, range(order, 0, -1)):
        if o == order:
            equation += f"{c:0.1f}"
        else:
            equation += f" {'-' if c < 0 else '+'} {abs(c):0.1f}"

        if o > 1:
            equation += f"$x^{o}$"
        elif o == 1:
            equation += "$x$"

    return equation


# Global actions
plt.rcParams.update({"font.size": 20})
plt.style.use(STYLE)

# Plot the placeholder
if PLACEHOLDER_RUN:
    # Data generation
    if PLACEHOLDER_RANDOM_SEED:
        PLACEHOLDER_SEED = np.random.randint(0, 3000000)
        print(PLACEHOLDER_SEED)

    np.random.seed(PLACEHOLDER_SEED)

    x = np.linspace(0, 10, 100)
    y = [np.zeros(x.shape) for i in range(PLACEHOLDER_NUM_CURVE)]

    for data in y:
        for i in range(5):
            amp = np.random.uniform(-1, 1)
            freq = np.random.uniform(0.1, 2)
            is_sin = np.random.choice([True, False])
            data += amp * np.sin(freq * x) if is_sin else amp * np.cos(freq * x)

    # Generating the plot
    plt.figure()
    for data in y:
        plt.plot(x, data)
    plt.grid(True)
    plt.title(PLACEHOLDER_TITLE)
    plt.xlabel(PLACEHOLDER_XLABEL)
    plt.ylabel(PLACEHOLDER_YLABEL)
    plt.savefig(PLACEHOLDER_FILENAME, dpi=150, bbox_inches="tight")

# Plot the known x lin y lin
if KNOWN_XLIN_YLIN_RUN:
    # Data generation
    x = np.linspace(0, 2, 100)
    p = np.poly1d(KNOWN_XLIN_YLIN_COEFFS)
    y = p(x)

    # Generating the plot
    plt.figure()
    plt.plot(x, y)
    plt.grid(True)
    plt.title(coeffs_to_title(KNOWN_XLIN_YLIN_COEFFS))
    plt.xlabel(KNOWN_XLIN_YLIN_XLABEL)
    plt.ylabel(KNOWN_XLIN_YLIN_YLABEL)
    plt.savefig(KNOWN_XLIN_YLIN_FILENAME, dpi=150, bbox_inches="tight")

# Plot the known x log y lin
if KNOWN_XLOG_YLIN_RUN:
    # Data generation
    x = np.linspace(1, 5, 100)
    p = np.poly1d(KNOWN_XLOG_YLIN_COEFFS)
    y = p(x)

    # Generating the plot
    plt.figure()
    plt.plot(x, y)
    plt.grid(True)
    plt.title(coeffs_to_title(KNOWN_XLOG_YLIN_COEFFS))
    plt.xlabel(KNOWN_XLOG_YLIN_XLABEL)
    plt.ylabel(KNOWN_XLOG_YLIN_YLABEL)
    plt.xscale("log")
    plt.savefig(KNOWN_XLOG_YLIN_FILENAME, dpi=150, bbox_inches="tight")

# Plot the known x log y lin
if KNOWN_XLIN_YLOG_RUN:
    # Data generation
    x = np.linspace(0, 10, 100)
    p = np.poly1d(KNOWN_XLIN_YLOG_COEFFS)
    y = p(x)

    # Generating the plot
    plt.figure()
    plt.plot(x, y)
    plt.grid(True)
    plt.title(coeffs_to_title(KNOWN_XLIN_YLOG_COEFFS))
    plt.xlabel(KNOWN_XLIN_YLOG_XLABEL)
    plt.ylabel(KNOWN_XLIN_YLOG_YLABEL)
    plt.yscale("log")
    plt.savefig(KNOWN_XLIN_YLOG_FILENAME, dpi=150, bbox_inches="tight")

# Plot the known x log y lin
if KNOWN_XLOG_YLOG_RUN:
    # Data generation
    x = np.linspace(1, 10, 100)
    p = np.poly1d(KNOWN_XLOG_YLOG_COEFFS)
    y = p(x)

    # Generating the plot
    plt.figure()
    plt.plot(x, y)
    plt.grid(True)
    plt.title(coeffs_to_title(KNOWN_XLOG_YLOG_COEFFS))
    plt.xlabel(KNOWN_XLOG_YLOG_XLABEL)
    plt.ylabel(KNOWN_XLOG_YLOG_YLABEL)
    plt.xscale("log")
    plt.yscale("log")
    plt.savefig(KNOWN_XLOG_YLOG_FILENAME, dpi=150, bbox_inches="tight")
