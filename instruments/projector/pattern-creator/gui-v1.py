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

import scipy.misc
from skimage.draw import line, disk, rectangle

RES_Y = 1920
RES_X = 1080


def CreatePointsPattern(resolution_x=RES_Y, resolution_y=RES_X,
                        num_points_x=10,    num_points_y=10,
                        offset_x=0,         offset_y=0,
                        point_diameter=10,  point_shape="circle"):

    # Parameters for the pattern
    distance_x = int(resolution_x / num_points_x)
    distance_y = int(resolution_y / num_points_y)
    offbound_points_flag = False

    # Fill with zeros
    pattern = np.zeros((resolution_y, resolution_x)).astype(np.uint8)

    # Mask with points
    for i in range(num_points_y):
        # Calculate which row we're at
        row = int(i * (resolution_y - 1) / num_points_y) + offset_y
        for j in range(num_points_x):
            # Calculate which row we're at
            col = int(j * (resolution_x - 1) / num_points_x) + offset_x
            try:
                # Paint point with given diameter
                if point_shape == "square":
                    start = (row - int(point_diameter/2),
                             col - int(point_diameter/2))
                    end = (row + int(point_diameter/2),
                           col + int(point_diameter/2))
                    rr, cc = rectangle(start, end)
                    pattern[rr, cc] = 1
                elif point_shape == "circle":
                    rr, cc = disk((row, col), point_diameter)
                    pattern[rr, cc] = 1
            except:
                offbound_points_flag = True

    return pattern


def DrawLine(pattern, start, end):
    rr, cc = line(start[0], start[1], end[0], end[1])
    pattern[rr, cc] = 1
    print(rr)
    print(cc)

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


def SetPatternSequence(array, color, exposure):

    # If not connected, try to connect
    if (dlp.connected == False):
        dlp.TryConnection()

    try:
        dlp.stopsequence()
        dlp.changemode(3)

        # Set secondary parameters
        exposure = [exposure]*len(array)
        dark_time = [0]*len(array)
        trigger_in = [0]*len(array)
        trigger_out = [0]*len(array)
        repetitions = 0  # infinite loop

        # Start sequence
        dlp.defsequence(array, color, exposure, trigger_in,
                        dark_time, trigger_out, repetitions)
        dlp.startsequence()
    except:
        dlp.connected = False
        print("Projector not connected")


def SetPattern(pattern, color):

    # If not connected, try to connect
    if (dlp.connected == False):
        dlp.TryConnection()

    try:
        dlp.stopsequence()
        dlp.changemode(3)

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
    except:
        dlp.connected = False
        print("Projector not connected")


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
        self.projector_tab.header = QtWidgets.QLabel(self)
        self.projector_tab.header.setFont(font)
        self.projector_tab.header.setText("Projector Settings")
        self.projector_tab.header.move(160, 20)

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
        points_x_input.setValue(self.m.points_x)
        points_x_input.setRange(1, 1000)
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
        points_y_input.setValue(self.m.points_y)
        points_y_input.setRange(1, 1000)
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
        offset_x_input.setRange(0, 1000)
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
        offset_y_input.setRange(0, 1000)
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
        diameter_input.setValue(self.m.point_diameter)
        diameter_input.valueChanged.connect(self.pointDiameterChange)

        # Send pattern to the projector when the button is clicked
        button = QPushButton('Set Pattern', self)
        button.clicked.connect(self.m.setPattern)
        button.setToolTip('Send pattern to the projector')
        button.move(160 + 133 * 3, 500)
        button.resize(100, 30)

        self.show()

    def colorChange(self, color):
        self.m.point_color = color
        cmap = matplotlib.colors.ListedColormap(
            ['none', to_rgb[self.m.point_color]])
        self.m.graph.set_cmap(cmap)
        self.m.fig.canvas.draw()

    def pointDiameterChange(self, value):
        self.m.point_diameter = value
        self.m.updateChart()

    def changeNumPointsX(self, value):
        self.m.points_x = value
        self.m.updateChart()

    def changeNumPointsY(self, value):
        self.m.points_y = value
        self.m.updateChart()

    def changeOffsetX(self, value):
        self.m.offset_x = value
        self.m.updateChart()

    def changeOffsetY(self, value):
        self.m.offset_y = value
        self.m.updateChart()


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
        self.point_diameter = 25
        self.points_x = 10
        self.points_y = 10
        self.offset_x = 0
        self.offset_y = 0

        # Initialize axes
        self.ax = self.figure.add_subplot(111)

        # Import grain boundary sample image and set as background
        # Resize to projector resolution (1920x1080)
        self.image = plt.imread("grain-boundaries/sample.png")
        self.ax.imshow(self.image, alpha=0.5, extent=[0, RES_Y, 0, RES_X])

        # Create pattern
        self.pattern = CreatePointsPattern(
            RES_Y, RES_X, self.points_x, self.points_y, self.offset_x, self.offset_y, self.point_diameter, "circle")

        # Custom binary colormap dependant on point_color selection
        cmap = matplotlib.colors.ListedColormap(
            ['none', to_rgb[self.point_color]])
        self.graph = self.ax.imshow(self.pattern, cmap=cmap)

        # Record coordinates when user clicks on the plot
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)

        # Hide axis ticks
        # self.ax.axes.xaxis.set_visible(False)
        # self.ax.axes.yaxis.set_visible(False)
        # self.ax.grid(True)

        self.draw()

    def updateChart(self):
        self.pattern = CreatePointsPattern(
            RES_Y, RES_X, self.points_x, self.points_y, self.offset_x, self.offset_y, self.point_diameter, "circle")
        self.graph.set_data(self.pattern)
        self.fig.canvas.draw()

    def setPattern(self):
        SetPattern(self.pattern, self.point_color)

    def onClick(self, event):
        print([int(event.xdata), int(event.ydata)])
        self.pattern = DrawLine(self.pattern, [100, 100], [
                                int(event.ydata), int(event.xdata)])
        self.graph.set_data(self.pattern)
        self.fig.canvas.draw()


if __name__ == '__main__':

    # Inititalize dmd
    dlp = projector.dmd()

    # Start GUI
    app = QApplication(sys.argv)
    QApplication.setStyle(ProxyStyle())
    app.setStyle("Fusion")
    ex = App()
    sys.exit(app.exec_())
