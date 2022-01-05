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
    POINTS_MATLAB = 3
    POINTS_PYTHON = 4
    POINTS_NUMPY = 5
    POINTS_CSV = 6
    COEFFS_MATLAB = 7
    COEFFS_PYTHON = 8
    COEFFS_NUMPY = 9
    POLY1D = 10


# APPLICATION DATA
VER = "2.3"
AUTHOR = "Bruno-Pier Busque"

APP_W = 1500
APP_H = 750

MAX_IMG_W = 1200
MAX_IMG_H = 730

# PATHS
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/"))
ICON_PATH = os.path.join(DATA_PATH, "icon.ico")
PH_IMAGE_PATH = os.path.join(DATA_PATH, "placeholder.png")
TEMP_PATH = os.path.join(DATA_PATH, "temp/")
ORIG_IMG = os.path.join(TEMP_PATH, "original_img.png")
COOR_IMG = os.path.join(TEMP_PATH, "coordinate_img.png")
ROTA_IMG = os.path.join(TEMP_PATH, "rotated_img.png")
CONT_IMG = os.path.join(TEMP_PATH, "contoured_img.png")
CTMK_IMG = os.path.join(TEMP_PATH, "masked_contoured_img.png")
SELE_IMG = os.path.join(TEMP_PATH, "selected_img.png")
PLOT_IMG = os.path.join(TEMP_PATH, "plotted_img.png")

# TEXTS
INITIAL_TEXT = "Select an image by pressing the `Select an image` button at the bottom and press `Start`."
STARTED_TEXT = "Click on 2 points for each axis in this order:\n\n" \
               "\tX1 -> X2 -> Y1 -> Y2\n" \
               "Enter their coordinates in the boxes below."
FILTER_CHOICE_TEXT = "Adjust the thresholding so that the curve you want to extract " \
                     "is clearly visible and free of nearby obstacles.\n\n" \
                     "When done, press `Next`"
EDGE_SELECTION_TEXT = "Press and hold the left mouse button over the curve you want to extract. All the " \
                      '"painted" multi-colored points will be extracted.\n\n'\
                      "If you wish to cancel some point that are painted, simply press and hold the right " \
                      "mouse button over the curve. \n\n"\
                      "When you selected all the curve, press `Next` to extract " \
                      "the data points."
EQUATION_TEXT = ""

# COPY OPTIONS
COPY_OPTIONS_TEXT = ("Copy Formula - Matlab", "Copy Formula - Python", "Copy Formula - Markdown",
                     "Copy Points - Matlab", "Copy Points - Python", "Copy Points - NumPy", "Copy Points - CSV",
                     "Copy Coeff. - Matlab", "Copy Coeff. - Python", "Copy Coeff. - NumPy", "Copy Poly1D - NumPy")
