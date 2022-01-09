from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, \
    QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from .widgets import QImage, QInstructBox, QImageOptions, QCoord
from .tools import get_copy_text, CurveFinder
from .constants import *

from random import randrange
from shutil import rmtree
from typing import List
import numpy as np
import cv2
import os


class QCurveFinder(QWidget):
    """ The application in itself """

    def __init__(self) -> None:
        """ Initialise the app """
        QWidget.__init__(self)

        # Set class variables
        self.curvefinder: CurveFinder
        self.img_src: str = PH_IMAGE_PATH
        self.coord: np.ndarray = np.zeros(4, dtype=float)
        self.pts_final_p: List[np.ndarray] = []
        self.pts_final_r: List[np.ndarray] = []
        self.pts_eval_r: List[np.ndarray] = []
        self.coef: list = []
        self.order: int = 5
        self.var: str = "x"
        self.islog: List[bool] = [False, False]
        self.mask: np.ndarray = None

        self.setWindowTitle(f"CurveFinder v{VER}")
        self.setWindowIcon(QIcon(ICON_PATH))
        self.setFixedWidth(APP_W)
        self.setFixedHeight(APP_H)

        # Create a temporary and data folder
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)
        if not os.path.exists(TEMP_PATH):
            os.mkdir(TEMP_PATH)

        # Create widgets
        self.img: QImage = QImage(PH_IMAGE_PATH)
        self.instruct: QInstructBox = QInstructBox()
        self.img_op: QImageOptions = QImageOptions()
        self.coord_prompt: QCoord = QCoord()
        self.but_browse: QPushButton = QPushButton(text="Select an image")
        self.but_start: QPushButton = QPushButton(text="Start")
        self.but_next: QPushButton = QPushButton(text="Next")

        # Bind the signals
        self.img.signal.connect(self.add_position)
        self.but_browse.clicked.connect(self.browse_for_image)
        self.but_start.clicked.connect(self.start)
        self.but_next.clicked.connect(self.next)
        self.instruct.but_copy.clicked.connect(self.copy_text)
        self.img_op.combo.currentTextChanged.connect(self.update_image)
        self.img_op.slider1.sliderMoved.connect(self.update_image)
        self.img_op.slider2.sliderMoved.connect(self.update_image)
        self.img_op.spinbox.valueChanged.connect(self.set_equation)
        self.img_op.spinbox.valueChanged.connect(self.img.update_brush_radius)
        self.img_op.y_from_x.toggled.connect(self.set_equation)
        self.img_op.x_from_y.toggled.connect(self.set_equation)
        self.img_op.x_lin.toggled.connect(self.update_lin_log)
        self.img_op.x_log.toggled.connect(self.update_lin_log)
        self.img_op.y_lin.toggled.connect(self.update_lin_log)
        self.img_op.y_log.toggled.connect(self.update_lin_log)

        # Create the layout
        options = QVBoxLayout()
        options.addLayout(self.instruct)
        options.addLayout(self.img_op)
        options.addLayout(self.coord_prompt)
        options.addWidget(self.but_browse)
        but_lay = QHBoxLayout()
        but_lay.addWidget(self.but_start)
        but_lay.addWidget(self.but_next)
        options.addLayout(but_lay)

        hbox = QHBoxLayout()
        hbox.addWidget(self.img, alignment=Qt.AlignCenter, stretch=4)
        hbox.addLayout(options, stretch=1)

        self.setLayout(hbox)

        # Set application state
        self.app_state = AppState.INITIAL

        self.show()

    def __del__(self) -> None:
        """ Remove the temporary folder """
        rmtree(TEMP_PATH)

    def browse_for_image(self) -> None:
        """ Method to select an image """
        src = str(QFileDialog().getOpenFileName(filter="Images (*.png *.bmp *.jpg)")[0])
        if src != "":
            self.img_src = src
            self.img.source = self.img_src
            self.app_state = AppState.INITIAL  # Return to initial state

    def start(self) -> None:
        """ Method for the Start button """
        cv2.imwrite(ORIG_IMG, cv2.imread(self.img_src))
        self.app_state = AppState.STARTED

    def next(self) -> None:
        """ Method for the next button. It changes the state of the app """
        if self.app_state == AppState.COORD_ALL_SELECTED and self.verify_coord():
            self.app_state = AppState.FILTER_CHOICE
        elif self.app_state == AppState.FILTER_CHOICE:
            self.app_state = AppState.EDGE_SELECTION
        elif self.app_state == AppState.EDGE_SELECTION:
            self.app_state = AppState.EQUATION_IMAGE
        elif self.app_state == AppState.EQUATION_IMAGE:
            self.app_state = AppState.EQUATION_PLOT
        elif self.app_state == AppState.EQUATION_PLOT:
            self.app_state = AppState.EQUATION_IMAGE

    def verify_coord(self) -> bool:
        """ Method to verify if the coordinates are entered in the input boxes """
        good_coord = True
        for (i, coord) in enumerate([self.coord_prompt.x1_coord, self.coord_prompt.x2_coord,
                                     self.coord_prompt.y1_coord, self.coord_prompt.y2_coord]):
            try:
                self.coord[i] = float(coord.line.text())
            except ValueError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setText(f"Coordinates of {coord.coord_label} must be an number!")
                msgBox.setWindowTitle("Warning")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()
                good_coord = False
                break

        return good_coord

    def add_position(self, x: int, y: int, button: Qt.MouseButton) -> None:
        """ Method used when clicking with the mouse on the image """
        if self.app_state == AppState.STARTED:
            if not self.coord_prompt.x1_done:
                self.coord_prompt.pts[0] = (x, y)
                self.coord_prompt.x1_done = True
            elif not self.coord_prompt.x2_done:
                self.coord_prompt.pts[1] = (x, y)
                self.coord_prompt.x2_done = True
            elif not self.coord_prompt.y1_done:
                self.coord_prompt.pts[2] = (x, y)
                self.coord_prompt.y1_done = True
            elif not self.coord_prompt.y2_done:
                self.coord_prompt.pts[3] = (x, y)
                self.coord_prompt.y2_done = True
                self.app_state = AppState.COORD_ALL_SELECTED

        elif self.app_state == AppState.EDGE_SELECTION:
            if button == Qt.MouseButton.LeftButton:
                self.draw_mask(x, y, 255)
            elif button == Qt.MouseButton.RightButton:
                self.draw_mask(x, y, 1)

    def draw_mask(self, x: int, y: int, color: int) -> None:
        """ Method to draw the brush on the image """
        radius = self.img_op.spinbox.value()
        cv2.circle(self.mask, (x, y), radius, color, -1)

    def resize_and_rotate(self) -> None:  # TODO: Dewarp the image
        """ Method to rotate the image after the coordinate are confirmed. """
        img = cv2.imread(self.img_src)
        rot_matrix = self.curvefinder.get_rotation_matrix()
        img = cv2.warpAffine(img, rot_matrix, img.shape[1::-1], flags=cv2.INTER_LINEAR)

        cv2.imwrite(ROTA_IMG, img)
        self.img.source = ROTA_IMG

        self.update_lin_log()

    def update_lin_log(self):
        """
        Method to update the axis to a log or a linear and
        make the relation between graph and pixel space.
        """
        ready_to_update = self.app_state >= AppState.FILTER_CHOICE
        if ready_to_update:
            self.curvefinder.update_lin_log(self.img_op.x_lin.isChecked(), self.img_op.y_lin.isChecked(),
                                            ready_to_update)
            self.set_equation()

    def set_equation(self, do: bool = True) -> None:
        """ Method to update the equation displayed in the instruction box """
        if do and self.app_state >= AppState.EQUATION_IMAGE:
            if self.img_op.x_lin.isChecked():
                x = np.array(self.pts_final_r)[:, 0]
                x_log = False
            else:
                x = np.log10(self.pts_final_r)[:, 0]
                x_log = True
            if self.img_op.y_lin.isChecked():
                y = np.array(self.pts_final_r)[:, 1]
                y_log = False
            else:
                y = np.log10(self.pts_final_r)[:, 1]
                y_log = True

            if self.img_op.y_from_x.isChecked():
                var = "x"
                a = x
                b = y
                a_log = x_log
                b_log = y_log
            else:
                var = "y"
                a = y
                b = x
                a_log = y_log
                b_log = x_log

            self.var = var
            self.islog = [a_log, b_log]
            self.order = order = self.img_op.spinbox.value()
            self.coef = coef = np.polyfit(a, b, order)
            b = np.poly1d(coef)
            eval_a = np.linspace(min(a), max(a), 100)
            eval_b = b(eval_a)

            if a_log:
                eval_a = np.power(10, eval_a)
            if b_log:
                eval_b = np.power(10, eval_b)

            if var == "x":
                ex = eval_a
                ey = eval_b
            else:
                ex = eval_b
                ey = eval_a

            eval_pts = []
            for (x, y) in zip(ex, ey):
                eval_pts.append(np.array([x, y]))

            self.pts_eval_r = eval_pts

            equation = get_copy_text(CopyOptions.EQUATION_MARKDOWN, self.var, self.islog, self.coef,
                                     self.order, self.pts_final_r)

            text = "The equation for this curve is :\n\n" \
                   f"{equation}\n\n" \
                   "For more precision, use the copy function below."
            self.instruct.textbox.setMarkdown(text)

            if self.app_state == AppState.EQUATION_PLOT:
                self.plot_points()

    def update_image(self) -> None:
        """ Method to update the image with the contour chosen in the combobox """
        if self.app_state == AppState.FILTER_CHOICE:
            img = cv2.cvtColor(cv2.imread(ROTA_IMG), cv2.COLOR_BGR2GRAY)
            tr1, tr2 = [self.img_op.slider1.value(), self.img_op.slider2.value()]

            mode = self.img_op.combo.currentText()

            if mode == "Canny":
                img = cv2.Canny(img, tr1, tr2)
            elif mode == "Global Tresholding":
                img = cv2.medianBlur(img, 5)
                ret, img = cv2.threshold(img, tr1, tr2, cv2.THRESH_BINARY)
            elif mode == "Adaptive Mean Tresholding":
                img = cv2.medianBlur(img, 5)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
            elif mode == "Adaptive Gausian Tresholding":
                img = cv2.medianBlur(img, 5)
                img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            elif mode == "Otsu's Tresholding":
                ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            elif mode == "Otsu's Tresholding + Gausian Blur":
                img = cv2.GaussianBlur(img, (5, 5), 0)
                ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            else:
                pass

            cont, h = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
            a, b = img.shape
            img = np.zeros((a, b, 3))

            for c in cont:
                col = (randrange(255), randrange(255), randrange(255))
                cv2.drawContours(img, c, -1, col)

            cv2.imwrite(CONT_IMG, img)
            self.img.source = CONT_IMG

    def plot_points(self) -> None:
        """ Method to generate the plot image and display it """
        fig = Figure(figsize=(MAX_IMG_W/100, MAX_IMG_H/100), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.gca()

        x_true, y_true = [np.array(self.pts_final_r)[:, 0], np.array(self.pts_final_r)[:, 1]]
        x_eval, y_eval = [np.array(self.pts_eval_r)[:, 0], np.array(self.pts_eval_r)[:, 1]]
        ax.plot(x_true, y_true, 'or', label="Extracted")
        ax.plot(x_eval, y_eval, '-b', label="Evaluated")
        ax.legend()
        ax.grid()

        if self.img_op.x_lin.isChecked():
            ax.set_xscale('linear')
        else:
            ax.set_xscale('log')
        if self.img_op.y_lin.isChecked():
            ax.set_yscale('linear')
        else:
            ax.set_yscale('log')

        canvas.draw()  # draw the canvas, cache the renderer

        img = np.frombuffer(canvas.tostring_rgb(), dtype='uint8').reshape(MAX_IMG_H, MAX_IMG_W, 3)
        cv2.imwrite(PLOT_IMG, img)
        self.img.source = PLOT_IMG

    def copy_text(self) -> None:
        """ Method to copy certain data """
        text = get_copy_text(self.instruct.combo.currentIndex(), self.var, self.islog, self.coef,
                             self.order, self.pts_final_r)

        if text is not None:
            QApplication.clipboard().setText(text)

    @property
    def app_state(self) -> AppState:
        """ Method to get the current app state """
        return self._app_state

    @app_state.setter
    def app_state(self, state: AppState) -> None:
        """ Method where the sequence of the app is handled """
        self._app_state = state

        if state == AppState.INITIAL:
            """Starting state"""
            self.instruct.textbox.setMarkdown(INITIAL_TEXT)
            self.but_start.setText("Start")
            self.but_next.setText("Next")
            self.but_next.setEnabled(False)
            self.coord_prompt.initValues()
            self.instruct.setEnabled(False)
            self.img_op.setEnabled(True)
            self.img_op.is_brush = True
            self.img.clickEnabled = False
            self.img.zoomEnabled = False
            self.img.maskEnabled = False

            self.curvefinder = CurveFinder()

        elif state == AppState.STARTED:
            """Pressed Start"""
            self.instruct.textbox.setMarkdown(STARTED_TEXT)
            self.but_start.setText("Restart")
            self.but_next.setText("Next")
            self.but_next.setEnabled(True)
            self.coord_prompt.initValues()
            self.instruct.setEnabled(False)
            self.img_op.setEnabled(True)
            self.img_op.is_brush = True
            self.pts_final_p = []
            self.pts_final_r = []
            self.pts_eval_r = []
            self.img.source = ORIG_IMG
            self.img.clickEnabled = True
            self.img.coordEnabled = True
            self.img.zoomEnabled = True

        elif state == AppState.COORD_ALL_SELECTED:
            """Coordinate all selected"""
            self.img.clickEnabled = False
            self.img.coordEnabled = False
            self.img.zoomEnabled = False

        elif state == AppState.FILTER_CHOICE:
            """Chose the coord and rotated"""
            self.instruct.textbox.setMarkdown(FILTER_CHOICE_TEXT)
            self.curvefinder.set_coord_points(self.coord)
            self.curvefinder.set_axis_points(self.coord_prompt.pts)
            self.curvefinder.update()
            self.resize_and_rotate()
            self.update_image()

        elif state == AppState.EDGE_SELECTION:
            """Chose the displaying"""
            self.instruct.textbox.setMarkdown(EDGE_SELECTION_TEXT)
            self.img_op.setEnabled(False)
            self.img.clickEnabled = True
            self.img.maskEnabled = True
            img = cv2.cvtColor(cv2.imread(CONT_IMG), cv2.COLOR_BGR2GRAY)
            img = np.greater(img, np.zeros(img.shape))*255  # Create the contour mask
            self.mask = np.ones(img.shape)
            cv2.imwrite(CTMK_IMG, img)

        elif state == AppState.EQUATION_IMAGE:
            """Selected the edges to keep"""
            self.img.clickEnabled = False
            self.img.maskEnabled = False
            img = cv2.cvtColor(cv2.imread(CTMK_IMG), cv2.COLOR_BGR2GRAY)
            img = np.equal(img, self.mask)
            pts_y, pts_x = np.where(img)

            img = cv2.imread(ROTA_IMG)
            for (x, y) in zip(pts_x, pts_y):
                a, b = self.curvefinder.pixel_to_graph((x, y))
                self.pts_final_p.append((x, y))
                self.pts_final_r.append(np.array([a, b]))
                cv2.circle(img, (x, y), 2, (0, 0, 255), -1)

            cv2.imwrite(SELE_IMG, img)
            self.img.source = SELE_IMG
            self.img.draw_points(self.curvefinder.get_points())
            self.instruct.setEnabled(True)
            self.img_op.is_brush = False
            self.set_equation()
            self.but_next.setText("Plot")

        elif state == AppState.EQUATION_PLOT:
            """Ready to plot"""
            self.but_next.setText("Image")
            self.plot_points()
