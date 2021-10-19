import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
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
        self.data_to_graph = data[frameNum, :, :, IQProperty]

        # Initialize main plot
        self.main = self.fig.add_subplot(10, 10, (1, 10*8-2))
        self.main.imshow(self.data_to_graph)

        # Calculate maximum value
        max_val = np.amax(self.data_to_graph)

        # Initialize column plot
        self.col_g = self.fig.add_subplot(10, 10, (10, 10*8))
        self.col_graph, = self.col_g.plot(
            self.data_to_graph[:, 150], np.arange(300))  # Display vertically
        self.col_g.set_ylim([300, 0])
        self.col_g.set_xlim([max_val + 100, 0])
        self.col_g.yaxis.set_visible(False)
        self.col_g.xaxis.set_visible(False)

        # Initialize row plot
        self.row_g = self.fig.add_subplot(10, 10, (10*9+1, 10*10-2))
        self.row_graph, = self.row_g.plot(self.data_to_graph[150, :])
        self.row_g.set_ylim([0, max_val + 100])
        self.row_g.set_xlim([0, 300])
        self.row_g.yaxis.set_visible(False)
        self.row_g.xaxis.set_visible(False)

        # Record coordinates when user clicks on the plot
        self.fig.canvas.mpl_connect('button_press_event', self.OnClick)

        self.draw()

    def OnClick(self, event):
        row = int(event.ydata)
        self.row_graph.set_ydata(self.data_to_graph[row, :])
        col = int(event.xdata)
        self.col_graph.set_xdata(self.data_to_graph[:, col])
        self.draw()
