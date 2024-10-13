from PyQt5.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QTextBrowser,
    QSlider,
    QComboBox,
    QRadioButton,
    QSpinBox,
    QButtonGroup,
    QTabWidget,
    QWidget,
    QColorDialog,
)
from PyQt5.QtGui import (
    QPixmap,
    QMouseEvent,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QColor,
    QTextDocument,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QRectF, QSizeF

from typing import List, Tuple

from .constants import *


class QNewLabel(QLabel):
    def delete(self) -> None:
        self.setText("")
        self.setParent(None)


class QCoordBox(QHBoxLayout):
    """Subclass for the a single coordinate box"""

    def __init__(self, coord_label: str) -> None:
        """Initialise the single coordinate input box"""
        super().__init__()

        # Set the widgets
        self.coord_label: str = coord_label
        self.label: QNewLabel = QNewLabel(text=f"{coord_label} :")
        self.line: QLineEdit = QLineEdit()
        self.line.setPlaceholderText(f"Enter coord. for {coord_label}...")
        self.check: QCheckBox = QCheckBox(text=f"{coord_label} placed")
        self.check.setEnabled(False)

        # Create the layout
        self.addWidget(self.label)
        self.addWidget(self.line)
        self.addWidget(self.check)

    def delete(self) -> None:
        self.label.delete()
        self.line.setText("")
        self.line.setParent(None)
        self.check.setParent(None)
        self.setParent(None)


class QImage(QLabel):
    """The class for the big image box"""

    signal: pyqtSignal = pyqtSignal(int, int, Qt.MouseButton)
    zoom = 2
    radius = 60
    border: int = 3
    pts_colors: Tuple[QColor] = (
        QColor(204, 0, 0, 150),
        QColor(0, 153, 0, 150),
        QColor(0, 0, 153, 150),
        QColor(204, 204, 0, 150),
    )
    pts_labels: Tuple[str] = (
        "<p style='color:rgba(204, 0, 0, 150)'>X<sub>1</sub></p>",
        "<p style='color:rgba(0, 153, 0, 150)'>X<sub>2</sub></p>",
        "<p style='color:rgba(0, 0, 153, 150)'>Y<sub>1</sub></p>",
        "<p style='color:rgba(204, 204, 0, 150)'>Y<sub>2</sub></p>",
    )

    def __init__(self, image_path: str) -> None:
        """Initialise the image of the graph"""
        super().__init__()

        self.source: str = image_path  # Set the image

        self.clickEnabled: bool = False
        self.zoomEnabled: bool = False
        self.maskEnabled = False
        self.coordEnabled = False
        self.holding: bool = False
        self.button: Qt.MouseButton = Qt.MouseButton.NoButton
        self.setMouseTracking(True)

        self.setStyleSheet(f"border: {self.border}px solid gray;")  # Add borders

        self.base_pixmap: QPixmap = None
        self.updated_pixmap: QPixmap = None

        self.brush_radius: int = 5
        self.pts: List[QPoint, QPoint, QPoint, QPoint] = [None, None, None, None]

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        """Event when mouse is pressed on the image"""
        x, y = self.get_xy_from_event(ev)

        if self.clickEnabled:
            self.holding = True
            self.button = ev.button()
            if self.maskEnabled:
                self.add_mask(x, y)
            if self.coordEnabled:
                self.add_coord(x, y)
            self.emit_signal(ev)

    def mouseMoveEvent(self, ev: QMouseEvent) -> None:
        """Event when mouse is moved on the image"""
        x, y = self.get_xy_from_event(ev)

        if self.maskEnabled:
            self.add_mask(x, y)
            if self.holding:
                self.emit_signal(ev)

        if self.zoomEnabled:
            self.add_zoom(x, y)

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        """Event when mouse is released on the image"""
        self.holding = False
        self.button = Qt.MouseButton.NoButton

    def add_coord(self, x: int, y: int) -> None:
        if self.button == Qt.MouseButton.LeftButton:
            painter = QPainter(self.base_pixmap)

            # Set the pen for the point
            pen = QPen(self.pts_colors[self.num_printed_coord], 15)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawPoint(QPoint(x, y))

            # Draw text
            text = QTextDocument()
            text.setHtml(self.pts_labels[self.num_printed_coord])
            font = text.defaultFont()
            font.setPointSize(14)
            text.setDefaultFont(font)
            painter.translate(QPoint(x, y))
            text.drawContents(painter)
            painter.end()

            self.setPixmap(self.base_pixmap)

            self.pts[self.num_printed_coord] = QPoint(x, y)

            self.num_printed_coord += 1

    def add_mask(self, x: int, y: int) -> None:
        rectangle = QRect(
            QPoint(x - self.brush_radius, y - self.brush_radius),
            2 * self.brush_radius * QSize(1, 1),
        )
        overlay_pixmap = self.base_pixmap.copy(rectangle)
        crosshair_pixmap = self.base_pixmap.copy(rectangle)

        # If holding, add the mask
        if (
            self.holding
            and self.button == Qt.MouseButton.LeftButton
            or self.button == Qt.MouseButton.RightButton
        ):
            brush_painter = QPainter(overlay_pixmap)
            if self.button == Qt.MouseButton.LeftButton:
                pen = QPen(QColor(255, 0, 0, 100), 3 * self.brush_radius)
            elif self.button == Qt.MouseButton.RightButton:
                pen = QPen(QColor(255, 0, 0, 0), 3 * self.brush_radius)
            brush_painter.setPen(pen)
            brush_painter.drawPoint(overlay_pixmap.rect().center())
            brush_painter.end()

        # Add a contour to visualize where you paint
        crosshair_painter = QPainter(crosshair_pixmap)
        if self.holding and self.button == Qt.MouseButton.LeftButton:
            pen = QPen(QColor(255, 0, 0, 100), 3 * self.brush_radius)
            crosshair_painter.setPen(pen)
            crosshair_painter.drawPoint(overlay_pixmap.rect().center())
        crosshair_painter.setPen(QPen(QColor(255, 255, 255, 80), 3))
        crosshair_painter.drawEllipse(crosshair_pixmap.rect())
        crosshair_painter.end()

        path = QPainterPath()
        rectangle = QRectF(
            QPoint(x - self.brush_radius, y - self.brush_radius),
            2 * self.brush_radius * QSizeF(1, 1),
        )
        path.addEllipse(rectangle)

        # If holding, add the mask to the updated pixmap
        if self.holding:
            mask_painter = QPainter(self.updated_pixmap)
            mask_painter.setRenderHints(
                QPainter.Antialiasing | QPainter.SmoothPixmapTransform
            )
            mask_painter.setClipPath(path, Qt.IntersectClip)
            mask_painter.drawPixmap(
                QPoint(x - self.brush_radius, y - self.brush_radius), overlay_pixmap
            )
            mask_painter.end()

        # Add the crosshair to the pixmap
        rendered_pixmap = self.updated_pixmap.copy()
        final_crosshair_painter = QPainter(rendered_pixmap)
        final_crosshair_painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )
        final_crosshair_painter.setClipPath(path, Qt.IntersectClip)
        final_crosshair_painter.drawPixmap(
            QPoint(x - self.brush_radius, y - self.brush_radius), crosshair_pixmap
        )
        final_crosshair_painter.end()

        self.setPixmap(rendered_pixmap)

    def add_zoom(self, x: int, y: int) -> None:
        base_pixmap = self.base_pixmap.copy()
        rectangle = QRect(
            QPoint(x - self.radius / 2, y - self.radius / 2), self.radius * QSize(1, 1)
        )
        overlay_pixmap = base_pixmap.copy(rectangle).scaledToWidth(
            self.zoom * self.radius, Qt.SmoothTransformation
        )

        crosshair = QPainter(overlay_pixmap)
        crosshair.setPen(QPen(Qt.white, 3))
        crosshair.drawEllipse(overlay_pixmap.rect().center(), 3, 3)
        crosshair.setPen(QPen(Qt.black, 3))
        crosshair.drawEllipse(overlay_pixmap.rect().center(), 1, 1)
        crosshair.drawPoint(overlay_pixmap.rect().center())
        crosshair.drawEllipse(overlay_pixmap.rect())
        crosshair.end()

        rectangle_zoomed = QRectF(QPoint(x, y), self.zoom * self.radius * QSizeF(1, 1))
        path = QPainterPath()
        path.addEllipse(rectangle_zoomed)

        painter = QPainter(base_pixmap)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setClipPath(path, Qt.IntersectClip)
        painter.drawPixmap(QPoint(x, y), overlay_pixmap)
        painter.end()

        self.setPixmap(base_pixmap)

    def draw_points(self, pts: Tuple[Tuple[float, float], ...]) -> None:
        for i, pt in enumerate(pts):
            x, y = pt
            self.pts[i] = QPoint(int(x), int(y))

        for pt, color, label in zip(self.pts, self.pts_colors, self.pts_labels):
            painter = QPainter(self.base_pixmap)
            # Set the pen for the point
            pen = QPen(color, 15)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            painter.drawPoint(pt)

            # Draw text
            text = QTextDocument()
            text.setHtml(label)
            font = text.defaultFont()
            font.setPointSize(14)
            text.setDefaultFont(font)
            painter.translate(pt)
            text.drawContents(painter)

            painter.end()

        self.setPixmap(self.base_pixmap)

    def update_brush_radius(self, value: int) -> None:
        self.brush_radius = value

    def emit_signal(self, ev: QMouseEvent) -> None:
        x, y = self.get_xy_from_event(ev)
        self.signal.emit(x, y, self.button)

    def get_xy_from_event(self, ev: QMouseEvent) -> Tuple[int, int]:
        return ev.x() - self.border, ev.y() + self.border

    @property
    def maskEnabled(self) -> bool:
        """Return if maskEnable is true or not"""
        return self._maskEnabled

    @maskEnabled.setter
    def maskEnabled(self, a0: bool) -> None:
        """Set the maskEnable attribute"""
        self._maskEnabled = a0
        self.updated_pixmap = self.source.copy()

    @property
    def coordEnabled(self) -> bool:
        """Return if coordEnable is true or not"""
        return self._coordEnabled

    @coordEnabled.setter
    def coordEnabled(self, a0: bool) -> None:
        """Set the coordEnable attribute"""
        self._coordEnabled = a0
        self.updated_pixmap = self.source.copy()
        self.num_printed_coord = 0

    @property
    def source(self) -> QPixmap:
        """Return the image"""
        return self._source

    @source.setter
    def source(self, src: str) -> None:
        """Set the image and resize it to fit in the box"""
        self.img_path = src  # Save the path
        new_img = QPixmap(src)  # Load the image
        self._source = new_img.scaled(
            MAX_IMG_W, MAX_IMG_H, Qt.KeepAspectRatio
        )  # Save the rescaled source image
        self.image_size = (self._source.height(), self._source.width())
        self._source.save(src)  # Save the resized image
        self.setPixmap(self._source)  # Display the image
        self.base_pixmap = self._source.copy()


class QInstructBox(QVBoxLayout):
    """Class for the instruction box widget"""

    def __init__(self) -> None:
        """Initialise the Instruction box"""
        super().__init__()

        # Create the  widgets
        self.label = QNewLabel(text="Instructions :")
        self.label.setFont(QFont("Helvetica", 14, QFont.Bold))

        self.textbox: QTextBrowser = QTextBrowser()
        self.textbox.setFont(QFont("Calibri", 12, QFont.Bold))

        # Create the layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.textbox)

        self.addLayout(vbox)


class QOptionsTemplate(QVBoxLayout):
    def __init__(self, main_label: str) -> None:
        super().__init__()

        # Create the  widgets
        self.main_label = QNewLabel(main_label)
        self.main_label.setFont(QFont("Helvetica", 14, QFont.Bold))

        # Create the layout
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.main_label)

        self.addLayout(self.vbox)

    def delete(self) -> None:
        self.main_label.delete()

        self.setParent(None)


class QCoordOption(QOptionsTemplate):
    """The class for the coordinate inputs box"""

    pts_labels: Tuple[str] = ("X1", "X2", "Y1", "Y2")

    def __init__(self) -> None:
        """Initialise the coordinate inputs"""
        super().__init__("Coordinates :")

        # Init the pts and them characteristics
        self.pts: List[Tuple[int, int]] = [(-1, -1)] * 4

        # Create the widgets
        self.x1_coord: QCoordBox = QCoordBox(self.pts_labels[0])
        self.x2_coord: QCoordBox = QCoordBox(self.pts_labels[1])
        self.y1_coord: QCoordBox = QCoordBox(self.pts_labels[2])
        self.y2_coord: QCoordBox = QCoordBox(self.pts_labels[3])

        # Create the layout
        self.vbox.addLayout(self.x1_coord)
        self.vbox.addLayout(self.x2_coord)
        self.vbox.addLayout(self.y1_coord)
        self.vbox.addLayout(self.y2_coord)

        # Initialise the values
        self.initValues()

    def initValues(self) -> None:
        """Initialise the coordinate statuses"""
        self.x1_done = False
        self.x2_done = False
        self.y1_done = False
        self.y2_done = False

    @property
    def x1_done(self) -> bool:
        """Return if x1 is done"""
        return self._x1_done

    @x1_done.setter
    def x1_done(self, status: bool) -> None:
        """Set x1 and check the box"""
        self._x1_done = status
        self.x1_coord.check.setChecked(status)
        if not status:
            self.pts[0] = (-1, -1)

    @property
    def x2_done(self) -> bool:
        """Return if x2 is done"""
        return self._x2_done

    @x2_done.setter
    def x2_done(self, status: bool) -> None:
        """Set x2 and check the box"""
        self._x2_done = status
        self.x2_coord.check.setChecked(status)
        if not status:
            self.pts[1] = (-1, -1)

    @property
    def y1_done(self) -> bool:
        """Return if y1 is done"""
        return self._y1_done

    @y1_done.setter
    def y1_done(self, status: bool) -> None:
        """Set y1 and check the box"""
        self._y1_done = status
        self.y1_coord.check.setChecked(status)
        if not status:
            self.pts[2] = (-1, -1)

    @property
    def y2_done(self) -> bool:
        """Return if y2 is done"""
        return self._y2_done

    @y2_done.setter
    def y2_done(self, status: bool) -> None:
        """Set y2 and check the box"""
        self._y2_done = status
        self.y2_coord.check.setChecked(status)
        if not status:
            self.pts[3] = (-1, -1)

    def delete(self) -> None:
        self.x1_coord.delete()
        self.x2_coord.delete()
        self.y1_coord.delete()
        self.y2_coord.delete()
        super().delete()


class QContoursOption(QOptionsTemplate):
    treshs: Tuple[Tuple[bool]] = (
        (True, True),
        (True, True),
        (False, False),
        (False, False),
        (False, False),
        (False, False),
        (False, False),
    )
    tresh_ext: Tuple[Tuple[int]] = (
        (-1000, 1000, -1000, 1000),
        (0, 255, 0, 255),
        (0, 1, 0, 1),
        (0, 1, 0, 1),
        (0, 1, 0, 1),
        (0, 1, 0, 1),
        (0, 1, 0, 1),
    )

    def __init__(self) -> None:
        super().__init__("Contour options :")

        # Set the combobox
        self.label_combo: QNewLabel = QNewLabel(text="Contour :")
        self.combo: QComboBox = QComboBox()
        self.combo.addItems(CONTOUR_OPTIONS_TEXT)
        self.combo.currentTextChanged.connect(self.combo_change)

        # Set the first labeled slider
        self.label1: QNewLabel = QNewLabel(text="Thresh. 1 :")
        self.slider1: QSlider = QSlider(Qt.Horizontal)
        self.slider1.setMinimum(-1000)
        self.slider1.setMaximum(1000)
        self.slider1.setTickInterval(100)
        self.slider1.setTickPosition(QSlider.TicksBelow)

        # Set the second labeled slider
        self.label2: QNewLabel = QNewLabel(text="Thresh. 2 :")
        self.slider2: QSlider = QSlider(Qt.Horizontal)
        self.slider2.setMinimum(-1000)
        self.slider2.setMaximum(1000)
        self.slider2.setTickInterval(100)
        self.slider2.setTickPosition(QSlider.TicksBelow)

        # Set the layout
        self.vbox.addWidget(self.label_combo)
        self.vbox.addWidget(self.combo)
        self.vbox.addWidget(self.label1)
        self.vbox.addWidget(self.slider1)
        self.vbox.addWidget(self.label2)
        self.vbox.addWidget(self.slider2)

    def combo_change(self, text) -> None:
        """Method to change the slider values based on the combobox text"""
        for i, op in enumerate(CONTOUR_OPTIONS_TEXT):
            if text == op:
                self.slider1.setEnabled(self.treshs[i][0])
                self.slider1.setValue(0)
                self.slider1.setMinimum(self.tresh_ext[i][0])
                self.slider1.setMaximum(self.tresh_ext[i][1])
                self.slider2.setEnabled(self.treshs[i][1])
                self.slider2.setValue(0)
                self.slider2.setMinimum(self.tresh_ext[i][2])
                self.slider2.setMaximum(self.tresh_ext[i][3])

    def delete(self) -> None:
        self.label_combo.delete()
        self.combo.setParent(None)
        self.label1.delete()
        self.slider1.setParent(None)
        self.label2.delete()
        self.slider2.setParent(None)
        super().delete()


class QColorsOption(QOptionsTemplate):
    color_changed: pyqtSignal = pyqtSignal()

    def __init__(self) -> None:
        super().__init__("Color options :")

        # Set the combobox
        self.label_color: QNewLabel = QNewLabel(text="Color :")
        self.color: QColor = QColor(0, 0, 0, 255)
        self.rect_color = QNewLabel()
        self.rect_color.setGeometry(100, 100, 200, 60)
        self.rect_color.setWordWrap(True)
        self.rect_color.setAlignment(Qt.AlignCenter)
        self.change_color(False)
        self.but_color: QPushButton = QPushButton(text="Change")

        # Set the first labeled slider
        self.slider_label: QNewLabel = QNewLabel(text="Threshold :")
        self.slider: QSlider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(127)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)

        # Connect the signals
        self.but_color.clicked.connect(lambda: self.change_color(True))

        # Set the layout
        self.vbox.addWidget(self.label_color)
        col_hbox = QHBoxLayout()
        col_hbox.addWidget(self.rect_color)
        col_hbox.addWidget(self.but_color)
        self.vbox.addLayout(col_hbox)
        self.vbox.addWidget(self.slider_label)
        self.vbox.addWidget(self.slider)

    def change_color(self, dialog: bool = True) -> None:
        if dialog:
            self.color = QColorDialog.getColor()
            self.color_changed.emit()
        self.rect_color.setText(self.color.name())
        luminance = (
            0.299 * self.color.red()
            + 0.587 * self.color.green()
            + 0.114 * self.color.blue()
        ) / 255
        self.rect_color.setStyleSheet(
            "QLabel{border-style: outset;"
            "border-width: 2px;"
            "border-radius: 10px;"
            "border-color: black;"
            f"color: {'black' if luminance > 0.5 else 'white'}}}"
            f"QWidget{{background-color: {self.color.name():s};}}"
        )

    def delete(self) -> None:
        self.label_color.delete()
        self.rect_color.setParent(None)
        self.but_color.setParent(None)
        self.slider_label.delete()
        self.slider.setParent(None)
        super().delete()


class QFilterOption(QOptionsTemplate):
    def __init__(self) -> None:
        super().__init__("Filters :")

        # Add the widgets
        self.tabs: QTabWidget = QTabWidget()
        self.pages: List[QWidget] = [QWidget(), QWidget()]
        self.contours: QContoursOption = QContoursOption()
        self.colors: QColorsOption = QColorsOption()

        # Set the layout
        self.pages[0].setLayout(self.contours)
        self.pages[1].setLayout(self.colors)
        self.tabs.addTab(self.pages[0], "Contours")
        self.tabs.addTab(self.pages[1], "Colors")
        self.vbox.addWidget(self.tabs)

    def delete(self) -> None:
        self.contours.delete()
        self.colors.delete()
        self.tabs.setParent(None)
        super().delete()


class QEdgeSelectionOption(QOptionsTemplate):
    def __init__(self) -> None:
        super().__init__("Edge selection options :")

        # Create the widgets
        self.label: QNewLabel = QNewLabel("Brush size :")
        self.spinbox: QSpinBox = QSpinBox()
        self.spinbox.setRange(0, 100)
        self.spinbox.setSingleStep(5)

        # Set the layout
        hbox = QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.spinbox)
        self.vbox.addLayout(hbox)

    def delete(self) -> None:
        self.label.delete()
        self.spinbox.setParent(None)
        super().delete()


class QEvaluationOptions(QOptionsTemplate):
    def __init__(self) -> None:
        super().__init__("Evaluation options :")

        # Create the widgets
        self.combo: QComboBox = QComboBox()
        self.combo.addItems(COPY_OPTIONS_TEXT)
        self.but_copy: QPushButton = QPushButton(text="Copy")

        self.label1: QNewLabel = QNewLabel(text="Wanted equation :")
        self.bg_formula: QButtonGroup = QButtonGroup()
        self.y_from_x: QRadioButton = QRadioButton(text="y = f(x)")
        self.y_from_x.setChecked(True)
        self.x_from_y: QRadioButton = QRadioButton(text="x = f(y)")
        self.bg_formula.addButton(self.y_from_x)
        self.bg_formula.addButton(self.x_from_y)

        self.labelx: QNewLabel = QNewLabel(text="X-axis is :")
        self.bg_x: QButtonGroup = QButtonGroup()
        self.x_lin: QRadioButton = QRadioButton(text="Lin.")
        self.x_lin.setChecked(True)
        self.x_log: QRadioButton = QRadioButton(text="Log.")
        self.bg_x.addButton(self.x_lin)
        self.bg_x.addButton(self.x_log)

        self.labely: QNewLabel = QNewLabel(text="Y-axis is :")
        self.bg_y: QButtonGroup = QButtonGroup()
        self.y_lin: QRadioButton = QRadioButton(text="Lin.")
        self.y_lin.setChecked(True)
        self.y_log: QRadioButton = QRadioButton(text="Log.")
        self.bg_y.addButton(self.y_lin)
        self.bg_y.addButton(self.y_log)

        self.label2: QNewLabel = QNewLabel("Fit order :")
        self.spinbox: QSpinBox = QSpinBox()
        self.spinbox.setRange(0, 15)
        self.spinbox.setSingleStep(1)
        self.spinbox.setValue(5)

        self.label3: QNewLabel = QNewLabel("Input :")
        self.input: QLineEdit = QLineEdit()
        self.input.setPlaceholderText("x")
        self.output: QLineEdit = QLineEdit()
        self.output.setPlaceholderText("y")
        self.output.setEnabled(False)
        self.y_from_x.clicked.connect(lambda: self.input.setPlaceholderText("x"))
        self.y_from_x.clicked.connect(lambda: self.output.setPlaceholderText("y"))
        self.x_from_y.clicked.connect(lambda: self.input.setPlaceholderText("y"))
        self.x_from_y.clicked.connect(lambda: self.output.setPlaceholderText("x"))
        self.but_evaluate: QPushButton = QPushButton(text="Evaluate")

        # Set the layout
        hbcopy = QHBoxLayout()
        hbcopy.addWidget(self.combo)
        hbcopy.addWidget(self.but_copy)

        hb0 = QHBoxLayout()
        hb0.addWidget(self.label1)
        hb0.addStretch(1)
        hb0.addWidget(self.y_from_x)
        hb0.addWidget(self.x_from_y)

        hb1 = QHBoxLayout()
        hb1.addWidget(self.labelx)
        hb1.addWidget(self.x_lin)
        hb1.addWidget(self.x_log)
        hb1.addStretch(1)
        hb1.addWidget(self.labely)
        hb1.addWidget(self.y_lin)
        hb1.addWidget(self.y_log)

        hb2 = QHBoxLayout()
        hb2.addWidget(self.label2)
        hb2.addWidget(self.spinbox)

        hb3 = QHBoxLayout()
        hb3.addWidget(self.label3)
        hb3.addWidget(self.input)
        hb3.addWidget(self.output)
        hb3.addWidget(self.but_evaluate)

        self.vbox.addLayout(hbcopy)
        self.vbox.addLayout(hb0)
        self.vbox.addLayout(hb1)
        self.vbox.addLayout(hb2)
        self.vbox.addLayout(hb3)

    def delete(self) -> None:
        self.combo.setParent(None)
        self.but_copy.setParent(None)

        self.label1.delete()
        self.bg_formula.setParent(None)
        self.y_from_x.setParent(None)
        self.x_from_y.setParent(None)

        self.labelx.delete()
        self.bg_x.setParent(None)
        self.x_lin.setParent(None)
        self.x_log.setParent(None)

        self.labely.delete()
        self.bg_y.setParent(None)
        self.y_lin.setParent(None)
        self.y_log.setParent(None)

        self.label2.delete()
        self.spinbox.setParent(None)

        self.label3.delete()
        self.input.setParent(None)
        self.output.setParent(None)
        self.but_evaluate.setParent(None)

        super().delete()
