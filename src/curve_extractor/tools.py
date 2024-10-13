from typing import Union, List, Tuple
from numpy import ndarray, array
from .constants import *
from enum import Enum
import math as mt
import cv2


class CurveFinder:
    def __init__(self) -> None:
        self.graph = self.Graph()
        self.x1_graph: float = 0
        self.x2_graph: float = 0
        self.y1_graph: float = 0
        self.y2_graph: float = 0
        self.dx_pixel_to_graph: float = 0
        self.dy_pixel_to_graph: float = 0
        self.cx: float = 0
        self.cy: float = 0
        self.x_is_lin: bool = True
        self.y_is_lin: bool = True

    def set_coord_points(self, coords: ndarray) -> None:
        self.x1_graph, self.x2_graph, self.y1_graph, self.y2_graph = coords

    def set_axis_points(self, pts: List[Tuple[int, int]]) -> None:
        self.graph.x_axis.pts = ((pts[0][0], pts[0][1]), (pts[1][0], pts[1][1]))
        self.graph.y_axis.pts = ((pts[2][0], pts[2][1]), (pts[3][0], pts[3][1]))
        self.graph.update()

    def update(self) -> None:
        if self.x_is_lin:
            dx_graph = self.x2_graph - self.x1_graph
            x1_graph = self.x1_graph
        else:
            dx_graph = mt.log10(self.x2_graph) - mt.log10(self.x1_graph)
            x1_graph = mt.log10(self.x1_graph)

        dx_pixel = self.graph.x_axis.x2_pixel - self.graph.x_axis.x1_pixel
        self.dx_pixel_to_graph = dx_graph / dx_pixel
        self.cx = x1_graph - self.dx_pixel_to_graph * self.graph.x_axis.x1_pixel

        if self.y_is_lin:
            dy_graph = self.y2_graph - self.y1_graph
            y1_graph = self.y1_graph
        else:
            dy_graph = mt.log10(self.y2_graph) - mt.log10(self.y1_graph)
            y1_graph = mt.log10(self.y1_graph)

        dy_pixel = self.graph.y_axis.y2_pixel - self.graph.y_axis.y1_pixel
        self.dy_pixel_to_graph = dy_graph / dy_pixel
        self.cy = y1_graph - self.dy_pixel_to_graph * self.graph.y_axis.y1_pixel

    def update_lin_log(self, x_is_lin: bool, y_is_lin: bool, update_all: bool = True):
        self.x_is_lin = x_is_lin
        self.y_is_lin = y_is_lin
        if update_all:
            self.update()

    def get_rotation_matrix(self) -> ndarray:
        self.graph.update()
        return cv2.getRotationMatrix2D(
            self.graph.origin, 180 * self.graph.angle / mt.pi, 1
        )

    def get_points(self) -> Tuple[Tuple[float, float], ...]:
        return self.graph.get_points()

    def pixel_to_graph(self, pt: tuple) -> ndarray:
        """Method to convert a pixel coordinate to a graph coordinate"""
        x, y = pt

        a = self.dx_pixel_to_graph * x + self.cx
        if not self.x_is_lin:
            a = mt.pow(10, a)

        b = self.dy_pixel_to_graph * y + self.cy
        if not self.y_is_lin:
            b = mt.pow(10, b)

        return array([a, b])

    class Graph:
        axis_corner: Tuple[float, float]

        def __init__(self) -> None:
            self.x_axis = self.Axis(self.Axis.AxisType.X)
            self.y_axis = self.Axis(self.Axis.AxisType.Y)
            self.angle: float = None
            self.origin: Tuple[float, float] = None

        def update(self) -> None:
            # Update the angle
            self.angle = (self.x_axis.angle + self.y_axis.angle) / 2

            # Update the origin
            if self.y_axis.dx == 0:
                x0 = self.y_axis.pts[1][0]
            else:
                x0 = (
                    self.y_axis.slope * self.y_axis.pts[0][0]
                    - self.x_axis.slope * self.x_axis.pts[0][0]
                    + self.x_axis.pts[0][1]
                    - self.y_axis.pts[0][1]
                ) / (self.y_axis.slope - self.x_axis.slope)
            y0 = (
                self.x_axis.slope * (x0 - self.x_axis.pts[0][0]) + self.x_axis.pts[0][1]
            )
            self.origin = (x0, y0)

            # Update axis attributes
            self.x_axis.y0_pixel = y0
            self.x_axis.x1_pixel = x0 + (self.x_axis.pts[0][0] - x0) / mt.cos(
                self.angle
            )
            self.x_axis.x2_pixel = x0 + (self.x_axis.pts[1][0] - x0) / mt.cos(
                self.angle
            )

            self.y_axis.x0_pixel = x0
            self.y_axis.y1_pixel = y0 + (self.y_axis.pts[0][1] - y0) / mt.cos(
                self.angle
            )
            self.y_axis.y2_pixel = y0 + (self.y_axis.pts[1][1] - y0) / mt.cos(
                self.angle
            )

        def get_points(self) -> Tuple[Tuple[float, float], ...]:
            x_p = self.y_axis.x0_pixel
            x1_p = self.x_axis.x1_pixel
            x2_p = self.x_axis.x2_pixel
            y_p = self.x_axis.y0_pixel
            y1_p = self.y_axis.y1_pixel
            y2_p = self.y_axis.y2_pixel
            return (x1_p, y_p), (x2_p, y_p), (x_p, y1_p), (x_p, y2_p)

        class Axis:
            class AxisType(Enum):
                X = 0
                Y = 1

            def __init__(self, axis_type: AxisType):
                self.type = axis_type
                self.pts: Tuple[Tuple[int, int], Tuple[int, int]] = ((0, 0), (0, 1))
                self.slope: float
                self.angle: float
                self.x0_pixel: float = None
                self.x1_pixel: float = None
                self.x2_pixel: float = None
                self.y0_pixel: float = None
                self.y1_pixel: float = None
                self.y2_pixel: float = None

            @property
            def pts(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
                return self._pts

            @pts.setter
            def pts(self, pt: Tuple[Tuple[int, int], Tuple[int, int]]) -> None:
                self._pts = pt
                self.dx = pt[1][0] - pt[0][0]
                self.dy = pt[1][1] - pt[0][1]
                self.slope = mt.inf if self.dx == 0 else self.dy / self.dx
                if self.type == self.AxisType.X:
                    self.angle = mt.atan(self.slope)
                elif self.type == self.AxisType.Y:
                    self.angle = mt.atan(-1 / self.slope)


def get_copy_text(
    mode: CopyOptions, var: str, coefs: list, pts: List[ndarray]
) -> Union[str, None]:
    order = len(coefs) - 1
    equation = ""

    if mode == CopyOptions.EQUATION_MATLAB:
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c)}"

            if o > 1:
                equation += f"*{var}.^{o}"
            elif o == 1:
                equation += f"*{var}"

        return equation

    elif mode == CopyOptions.EQUATION_PYTHON:
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c)}"

            if o > 1:
                equation += f"*{var}**({o})"
            elif o == 1:
                equation += f"*{var}"

        return equation

    elif mode == CopyOptions.EQUATION_MARKDOWN:
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c:0.2e}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c):0.2e}"

            if o > 1:
                equation += f"{var}<sup>{o}</sup>"
            elif o == 1:
                equation += f"{var}"

        return equation

    elif mode == CopyOptions.EQUATION_LATEX:
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c:0.1f}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c):0.1f}"

            if o > 1:
                equation += f"x^{{{o}}}"
            elif o == 1:
                equation += "x"

        equation += "$"

        return equation

    elif mode == CopyOptions.EQUATION_EXCEL_LAMBDA_POINT:
        equation += f"=LAMBDA([{var}], "
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c)}"

            if o > 1:
                equation += f"*{var}^({o})"
            elif o == 1:
                equation += f"*{var}"

        equation += ")"
        return equation

    elif mode == CopyOptions.EQUATION_EXCEL_LAMBDA_COMMA:
        equation += f"=LAMBDA([{var}]; "
        for c, o in zip(coefs, range(order, -1, -1)):
            if o == order:
                equation += f"{c}"
            else:
                equation += f" {'-' if c < 0 else '+'} {abs(c)}"

            if o > 1:
                equation += f"*{var}^({o})"
            elif o == 1:
                equation += f"*{var}"

        equation += ")"
        equation = equation.replace(".", ",")
        return equation

    elif mode == CopyOptions.POINTS_MATLAB:
        text = "x = ["
        x_r = []
        y_r = []

        for d in pts:
            x_r.append(d[0])
            y_r.append(d[1])

        for i, x in enumerate(x_r):
            if i == 0:
                text += f"{x}"
            else:
                text += f" {x}"

        text += "];\ny = ["
        for i, y in enumerate(y_r):
            if i == 0:
                text += f"{y}"
            else:
                text += f" {y}"

        text += "];"

        return text

    elif mode == CopyOptions.POINTS_PYTHON:
        text = "x = ["
        x_r = []
        y_r = []

        for d in pts:
            x_r.append(d[0])
            y_r.append(d[1])

        for i, x in enumerate(x_r):
            if i == 0:
                text += f"{x}"
            else:
                text += f", {x}"

        text += "];\ny = ["
        for i, y in enumerate(y_r):
            if i == 0:
                text += f"{y}"
            else:
                text += f", {y}"

        text += "];"

        return text

    elif mode == CopyOptions.POINTS_NUMPY:
        text = "pts = np.array([["
        x_r = []
        y_r = []

        for d in pts:
            x_r.append(d[0])
            y_r.append(d[1])

        for i, x in enumerate(x_r):
            if i == 0:
                text += f"{x}"
            else:
                text += f", {x}"

        text += "], ["
        for i, y in enumerate(y_r):
            if i == 0:
                text += f"{y}"
            else:
                text += f", {y}"

        text += "]])"

        return text

    elif mode == CopyOptions.POINTS_CSV:
        text = "x, y\n"

        for d in pts:
            text += f"{d[0]}, {d[1]}\n"

        return text

    elif mode == CopyOptions.COEFFS_MATLAB:
        text = "["
        for i, coef in enumerate(coefs):
            if i == 0:
                text += f"{coef}"
            else:
                text += f" {coef}"
        text += "]"

        return text

    elif mode == CopyOptions.COEFFS_PYTHON:
        text = "["
        for i, coef in enumerate(coefs):
            if i == 0:
                text += f"{coef}"
            else:
                text += f", {coef}"
        text += "]"

        return text

    elif mode == CopyOptions.COEFFS_NUMPY:
        text = "np.array(["
        for i, coef in enumerate(coefs):
            if i == 0:
                text += f"{coef}"
            else:
                text += f", {coef}"
        text += "])"

        return text

    elif mode == CopyOptions.POLY1D:
        text = "p = np.poly1d(["
        for i, coef in enumerate(coefs):
            if i == 0:
                text += f"{coef}"
            else:
                text += f", {coef}"
        text += "])"

        return text

    else:
        return None
