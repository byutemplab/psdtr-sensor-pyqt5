import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.colors
import matplotlib.widgets
import numpy as np

from .libHeLIC import LibHeLIC


class CameraTab(QWidget):
    def __init__(self):
        super().__init__()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Camera Settings")
        self.header.move(30, 20)

        # Pattern preview from matplotlib
        self.m = PatternPlot(self, width=5, height=5)
        self.m.move(30, 80)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.m.setGraphicsEffect(shadow)

        self.show()


class PatternPlot(FigureCanvas):

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.parent = parent
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

    def plot(self):

        # Import data
        path = "camera\logs\intensity_img_2021_10_12-05_18_58_PM.npy"
        data = np.load(path)

        # Start by showing frame 0 and I parameter
        frameNum = 0
        IQProperty = 0

        # Initialize plot
        self.ax = self.fig.add_subplot(111)
        graph = self.ax.imshow(data[frameNum, :, :, IQProperty])
        self.draw()
