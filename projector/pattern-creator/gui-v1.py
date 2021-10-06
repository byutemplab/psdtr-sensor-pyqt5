import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QComboBox, QSpinBox, QGraphicsDropShadowEffect
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import QtWidgets, QtGui, QtCore


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.colors

import pycrafter6500 as projector
import numpy as np


# Returns a numpy array of size diameter x diameter with a circle mask
# For example, CreateCircleArray(5) returns:
# [[0 0 1 0 0]
#  [0 1 1 1 0]
#  [1 1 1 1 1]
#  [0 1 1 1 0]
#  [0 0 1 0 0]]


def CreateCircleArray(diameter):
    Y, X = np.ogrid[:diameter, :diameter]
    dist_from_center = np.sqrt((X - int(diameter / 2))**2
                               + (Y - int(diameter / 2))**2)
    mask = dist_from_center <= int(diameter / 2)

    return mask.astype(np.uint8)


def CreatePointsPattern(resolution_x=1920, resolution_y=1080,
                        num_points_x=10,   num_points_y=10,
                        offset_x=0,        offset_y=0,
                        point_diameter=10, point_shape="circle"):

    # Parameters for the pattern
    distance_x = int(resolution_x / num_points_x)
    distance_y = int(resolution_y / num_points_y)
    offbound_points_flag = False

    # Fill with zeros
    pattern = np.zeros((resolution_y, resolution_x)).astype(np.uint8)

    # Mask with points
    for i in range(resolution_y):
        for j in range(resolution_x):
            if (i - offset_y) % distance_y == 0 and (j - offset_x) % distance_x == 0:
                # Create point array
                if point_shape == "square":
                    point = np.ones((point_diameter, point_diameter))
                    point = point.astype(np.uint8)
                elif point_shape == "circle":
                    point = CreateCircleArray(point_diameter)
                # Replace with point array
                try:
                    pattern[i: i + point_diameter,
                            j: j + point_diameter] = point
                except:
                    offbound_points_flag = True

    return pattern


# Convert color to rgb
to_rgb = {
    'disabled': '#000000',
    'red':      '#ff0000',
    'green':    '#00ff00',
    'yellow':   '#ffff00',
    'blue':     '#0000ff',
    'magenta':  '#ff00ff',
    'cyan':     '#00ffff',
    'white':    '#9ae2f4',  # slightly blue to differentiate from white background
}


def SetPattern(pattern, color):

    # Append pattern to image array
    images = []
    images.append(pattern)

    # Set secondary parameters
    exposure = [0]*30
    dark_time = [0]*30
    trigger_in = [False]*30
    trigger_out = [1]*30

    # Start sequence
    dlp.defsequence(images, color, exposure, trigger_in,
                    dark_time, trigger_out, 0)
    dlp.startsequence()


class TabBar(QtWidgets.QTabBar):
    def tabSizeHint(self, index):
        s = QtWidgets.QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QtWidgets.QStylePainter(self)
        opt = QtWidgets.QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QtCore.QRect(QtCore.QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QtWidgets.QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class TabWidget(QtWidgets.QTabWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QtWidgets.QTabWidget.West)


class ProxyStyle(QtWidgets.QProxyStyle):
    def drawControl(self, element, opt, painter, widget):
        if element == QtWidgets.QStyle.CE_TabBarTabLabel:
            ic = self.pixelMetric(QtWidgets.QStyle.PM_TabBarIconSize)
            r = QtCore.QRect(opt.rect)
            w = 0 if opt.icon.isNull() else opt.rect.width() + \
                self.pixelMetric(QtWidgets.QStyle.PM_TabBarIconSize)
            r.setHeight(opt.fontMetrics.width(opt.text) + w)
            r.moveBottom(opt.rect.bottom())
            opt.rect = r
        QtWidgets.QProxyStyle.drawControl(self, element, opt, painter, widget)


class App(TabWidget):

    def __init__(self):
        super().__init__()
        self.left = 340
        self.top = 80
        self.title = 'TEMPLAB MSR Sensor'
        self.width = 700
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icons/msr-sensor-icon.png'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.projector_tab = QWidget()
        self.camera_tab = QWidget()
        self.addTab(self.projector_tab, QIcon(
            "icons/projector-icon.png"), "DMD Projector")
        self.addTab(self.camera_tab, QIcon(
            "icons/camera-icon.png"), "  Heliotis Camera")

        # Tab header
        font = QtGui.QFont()
        font.setPointSize(20)
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("Projector Settings")
        self.header.move(160, 20)

        # Pattern preview from matplotlib
        self.m = PlotCanvas(self, width=5, height=3)
        self.m.move(160, 80)
        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.m.setGraphicsEffect(shadow)

        # Set font for all small headers
        font = QtGui.QFont()
        font.setPointSize(10)

        # Number points x label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("# points x")
        self.header.move(160, 410)

        # Number points x
        points_x_input = QSpinBox(self)
        points_x_input.move(160, 430)
        points_x_input.resize(100, 30)
        points_x_input.setValue(4)
        points_x_input.valueChanged.connect(self.changeNumPointsX)

        # Number points y label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("# points y")
        self.header.move(160 + 133, 410)

        # Number points y
        points_y_input = QSpinBox(self)
        points_y_input.move(160 + 133, 430)
        points_y_input.resize(100, 30)
        points_y_input.setValue(4)
        points_y_input.valueChanged.connect(self.changeNumPointsY)

        # Offset x label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("Offset x")
        self.header.move(160 + 133 * 2, 410)

        # Offset x
        offset_x_input = QSpinBox(self)
        offset_x_input.move(160 + 133 * 2, 430)
        offset_x_input.resize(100, 30)
        offset_x_input.setValue(0)
        offset_x_input.valueChanged.connect(self.changeOffsetX)

        # Offset y label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("Offset y")
        self.header.move(160 + 133 * 3, 410)

        # Offset y
        offset_y_input = QSpinBox(self)
        offset_y_input.move(160 + 133 * 3, 430)
        offset_y_input.resize(100, 30)
        offset_y_input.setValue(0)
        offset_y_input.valueChanged.connect(self.changeOffsetY)

        # Color selection label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("Point color")
        self.header.move(160, 480)

        # Color Selection
        color_input = QComboBox(self)
        color_input.addItem("green")
        color_input.addItem("red")
        color_input.addItem("blue")
        color_input.addItem("white")
        color_input.move(160, 500)
        color_input.resize(100, 30)
        color_input.activated[str].connect(self.colorChange)

        # Point diameter selection label
        self.header = QtWidgets.QLabel(self)
        self.header.setFont(font)
        self.header.setText("Point diameter")
        self.header.move(160 + 133, 480)

        # Point diameter
        diameter_input = QSpinBox(self)
        diameter_input.move(160 + 133, 500)
        diameter_input.resize(100, 30)
        diameter_input.setRange(1, 1000)
        diameter_input.setValue(50)
        diameter_input.valueChanged.connect(self.pointDiameterChange)

        # Preview pattern
        button_preview = QPushButton('Update Preview', self)
        button_preview.clicked.connect(self.m.updateChart)
        button_preview.setToolTip('Preview pattern')
        button_preview.move(160 + 133 * 2, 500)
        button_preview.resize(100, 30)

        # Send pattern to the projector when the button is clicked
        button = QPushButton('Set Pattern', self)
        button.clicked.connect(self.m.setPattern)
        button.setToolTip('Send pattern to the projector')
        button.move(160 + 133 * 3, 500)
        button.resize(100, 30)

        self.show()

    def colorChange(self, color):
        self.m.point_color = color

    def pointDiameterChange(self, value):
        self.m.point_diameter = value

    def changeNumPointsX(self, value):
        self.m.points_x = value

    def changeNumPointsY(self, value):
        self.m.points_y = value

    def changeOffsetX(self, value):
        self.m.offset_x = value

    def changeOffsetY(self, value):
        self.m.offset_y = value


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):
        # Set initial parameters
        self.point_color = "green"
        self.point_diameter = 50
        self.points_x = 4
        self.points_y = 4
        self.offset_x = 0
        self.offset_y = 0
        self.pattern = CreatePointsPattern(
            1920, 1080, self.points_x, self.points_y, self.offset_x, self.offset_y, self.point_diameter, "circle")
        self.ax = self.figure.add_subplot(111)
        cmap = matplotlib.colors.ListedColormap(
            ['white', to_rgb[self.point_color]])
        self.ax.imshow(self.pattern, cmap=cmap)
        # self.ax.axes.xaxis.set_visible(False)
        # self.ax.axes.yaxis.set_visible(False)
        # self.ax.grid(True)
        self.draw()

    def updateChart(self):
        cmap = matplotlib.colors.ListedColormap(
            ['white', to_rgb[self.point_color]])
        self.pattern = CreatePointsPattern(
            1920, 1080, self.points_x, self.points_y, self.offset_x, self.offset_y, self.point_diameter, "circle")
        self.ax.imshow(self.pattern, cmap=cmap)
        self.fig.canvas.draw_idle()
        print("chart preview updated")

    def setPattern(self):
        self.pattern = CreatePointsPattern(
            1920, 1080, self.points_x, self.points_y, self.offset_x, self.offset_y, self.point_diameter, "circle")
        SetPattern(self.pattern, self.point_color)


if __name__ == '__main__':

    # Inititalize dmd in mode 3 (intentity visualizer)
    try:
        dlp = projector.dmd()
        dlp.stopsequence()
        dlp.changemode(3)
    except:
        print("Projector not connected")

    # Start GUI
    app = QApplication(sys.argv)
    QApplication.setStyle(ProxyStyle())
    app.setStyle("Fusion")
    ex = App()
    sys.exit(app.exec_())
