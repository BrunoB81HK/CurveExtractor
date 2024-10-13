from enum import IntEnum
import os


# ENUMS
class AppState(IntEnum):
    INITIAL = 0
    STARTED = 1
    COORD_ALL_SELECTED = 2
    FILTER_CHOICE = 3
    EDGE_SELECTION = 4
    EQUATION_IMAGE = 5
    EQUATION_PLOT = 6


class CopyOptions(IntEnum):
    EQUATION_MATLAB = 0
    EQUATION_PYTHON = 1
    EQUATION_MARKDOWN = 2
    EQUATION_LATEX = 3
    EQUATION_EXCEL_LAMBDA_POINT = 4
    EQUATION_EXCEL_LAMBDA_COMMA = 5
    POINTS_MATLAB = 6
    POINTS_PYTHON = 7
    POINTS_NUMPY = 8
    POINTS_CSV = 9
    COEFFS_MATLAB = 10
    COEFFS_PYTHON = 11
    COEFFS_NUMPY = 12
    POLY1D = 13


class ContourOptions(IntEnum):
    CANNY = 0
    GLOBAL = 1
    ADAPTIVE_MEAN = 2
    ADAPTIVE_GAUSSIAN = 3
    OTSUS = 4
    OTSUS_GAUSSIAN_BLUR = 5


# APPLICATION DATA
VER = "3.0"
AUTHOR = "Bruno-Pier Busque"

APP_WIDTH = 1500
APP_HEIGHT = 750

MAX_IMG_W = 1200
MAX_IMG_H = 730

# PATHS
RESOURCES_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../resources/")
)
ICON_PATH = os.path.join(RESOURCES_PATH, "icon.ico")
PH_IMAGE_PATH = os.path.join(RESOURCES_PATH, "placeholder.png")
TEMP_PATH = os.path.join(RESOURCES_PATH, "temp/")
ORIG_IMG = os.path.join(TEMP_PATH, "original_img.png")
COOR_IMG = os.path.join(TEMP_PATH, "coordinate_img.png")  # TODO: Not used anymore
ROTA_IMG = os.path.join(TEMP_PATH, "rotated_img.png")
CONT_IMG = os.path.join(TEMP_PATH, "contoured_img.png")
COLO_IMG = os.path.join(TEMP_PATH, "colored_img.png")
CTMK_IMG = os.path.join(TEMP_PATH, "masked_contoured_img.png")
SELE_IMG = os.path.join(TEMP_PATH, "selected_img.png")
PLOT_IMG = os.path.join(TEMP_PATH, "plotted_img.png")

# TEXTS
INITIAL_TEXT = "Select an image by pressing the `Select an image` button at the bottom and press `Start`."
STARTED_TEXT = (
    "Click on 2 points for each axis in this order:\n\n"
    "\tX1 -> X2 -> Y1 -> Y2\n"
    "Enter their coordinates in the boxes below."
)
FILTER_CHOICE_TEXT = (
    "Adjust the image so that the curve you want to extract "
    "is clearly visible and free of nearby obstacles. You can achieve this"
    "with either the contours or the colors mode.\n\n"
    "When done, press `Next`"
)
EDGE_SELECTION_TEXT = (
    "Press and hold the left mouse button over the curve you want to extract. All the "
    '"painted" multi-colored points will be extracted.\n\n'
    "If you wish to cancel some point that are painted, simply press and hold the right "
    "mouse button over the curve. \n\n"
    "When you selected all the curve, press `Next` to extract "
    "the data points."
)
EQUATION_TEXT = ""

# COPY OPTIONS
COPY_OPTIONS_TEXT = (
    "Equation - Matlab",
    "Equation - Python",
    "Equation - Markdown",
    "Equation - Latex",
    "Equation - Excel lambda (point)",
    "Equation - Excel lambda (comma)",
    "Points - Matlab",
    "Points - Python",
    "Points - NumPy",
    "Points - CSV",
    "Coeff. - Matlab",
    "Coeff. - Python",
    "Coeff. - NumPy",
    "Poly1D - NumPy",
)

CONTOUR_OPTIONS_TEXT = (
    "Canny",
    "Global Thresholding",
    "Adaptive Mean Thresholding",
    "Adaptive Gaussian Thresholding",
    "Otsu's Thresholding",
    "Otsu's Thresholding + Gaussian Blur",
)
