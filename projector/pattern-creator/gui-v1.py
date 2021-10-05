import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QComboBox, QSpinBox
from PyQt5.QtGui import QIcon


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


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 100
        self.top = 100
        self.title = 'Projector Pattern Settings'
        self.width = 640
        self.height = 400
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.m = PlotCanvas(self, width=5, height=4)
        self.m.move(0, 0)

        # Color Selection
        comboBox = QComboBox(self)
        comboBox.addItem("green")
        comboBox.addItem("red")
        comboBox.addItem("blue")
        comboBox.addItem("white")
        comboBox.move(500, 0)
        comboBox.resize(140, 60)
        comboBox.activated[str].connect(self.colorChange)

        # Point diameter
        diameter_input = QSpinBox(self)
        diameter_input.move(500, 80)
        diameter_input.resize(140, 60)
        diameter_input.setRange(1, 1000)
        diameter_input.setValue(50)
        diameter_input.valueChanged.connect(self.pointDiameterChange)

        # Preview pattern
        button_preview = QPushButton('Preview', self)
        button_preview.clicked.connect(self.m.updateChart)
        button_preview.setToolTip('Preview pattern')
        button_preview.move(500, 160)
        button_preview.resize(140, 60)

        # Send pattern to the projector when the button is clicked
        button = QPushButton('Set pattern', self)
        button.clicked.connect(self.m.setPattern)
        button.setToolTip('Send pattern to the projector')
        button.move(500, 240)
        button.resize(140, 60)

        self.show()

    def colorChange(self, color):
        self.m.point_color = color

    def pointDiameterChange(self, value):
        self.m.point_diameter = value


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
        self.pattern = CreatePointsPattern(
            1920, 1080, 4, 2, 0, 0, self.point_diameter, "circle")
        self.ax = self.figure.add_subplot(111)
        cmap = matplotlib.colors.ListedColormap(
            ['white', to_rgb[self.point_color]])
        self.ax.imshow(self.pattern, cmap=cmap)
        self.draw()

    def updateChart(self):
        cmap = matplotlib.colors.ListedColormap(
            ['white', to_rgb[self.point_color]])
        self.pattern = CreatePointsPattern(
            1920, 1080, 4, 2, 0, 0, self.point_diameter, "circle")
        self.ax.imshow(self.pattern, cmap=cmap)
        self.fig.canvas.draw_idle()
        print("chart preview updated")

    def setPattern(self):
        pattern = CreatePointsPattern(
            1920, 1080, 4, 2, 0, 0, self.point_diameter, "circle")
        SetPattern(pattern, self.point_color)


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
    ex = App()
    sys.exit(app.exec_())
