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

import cv2


class AnalysisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Data Analysis")
        self.header.move(30, 20)

        # Pattern preview from matplotlib
        self.plot = PatternPlot(self, width=5, height=5)
        self.plot.move(30, 80)

        # Navigation toolbar for graph
        self.toolbar = NavigationToolbar(self.plot, self)
        self.toolbar.move(22, 600)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.plot.setGraphicsEffect(shadow)

        # Start/stop pattern
        self.sample_animation_btn = QPushButton('Stream', self)
        self.sample_animation_btn.setCheckable(True)
        self.sample_animation_btn.clicked.connect(self.plot.RunSampleAnimation)
        self.sample_animation_btn.setToolTip(
            'Start showing data')
        self.sample_animation_btn.move(30 + 133 * 3, 620)
        self.sample_animation_btn.resize(100, 30)


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

        # Find dot position
        # image = self.data_to_graph.astype('uint8')
        # circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 100)
        # print(circles)

        # if circles is not None:
        #     # convert the (x, y) coordinates and radius of the circles to integers
        #     circles = np.round(circles[0, :]).astype("int")
        #     for (x, y, r) in circles:
        #         self.main.add_patch(
        #             matplotlib.pyplot.Circle((x, y), r, fill=False))

        self.draw()

    def RunSampleAnimation(self):
        if(self.parent.sample_animation_btn.isChecked() == True):
            self.graph = self.main.imshow(self.data_to_graph)

            def UpdateFig(*args):
                self.data_to_graph = np.rot90(self.data_to_graph)
                self.graph.set_array(self.data_to_graph)
                return self.graph,

            # Set animation
            self.animation = matplotlib.animation.FuncAnimation(
                self.fig, UpdateFig, interval=200, blit=True)

            self.draw()
        else:
            # Pause animation
            self.animation.pause()
