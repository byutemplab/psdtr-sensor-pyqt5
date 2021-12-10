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
from datetime import datetime

import cv2

from .imageprocessing import Scan

CAMERA_CONNECTED = True


class HelicamTab(QWidget):
    def __init__(self):
        super().__init__()
        if (CAMERA_CONNECTED):
            self.scan = Scan()
            self.scan.InitCamera()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Camera Settings")
        self.header.setContentsMargins(0, 10, 0, 10)

        # Pattern preview from matplotlib
        self.plot = PatternPlot(self, width=5, height=5)
        self.plot.move(30, 80)

        # Navigation toolbar for graph
        self.toolbar = NavigationToolbar(self.plot, self)
        self.toolbar.move(22, 600)
        self.toolbar.resize(10, 10)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.plot.setGraphicsEffect(shadow)

        # Save data
        self.save_btn = QPushButton('Save file', self)
        self.save_btn.clicked.connect(self.SaveStream)
        self.save_btn.setToolTip(
            'Save streaming data')
        self.save_btn.move(30 + 133 * 2, 620)
        self.save_btn.resize(100, 30)

        # Start/stop pattern
        self.sample_animation_btn = QPushButton('Stream', self)
        self.sample_animation_btn.setCheckable(True)
        self.sample_animation_btn.clicked.connect(self.plot.RunSampleAnimation)
        self.sample_animation_btn.setToolTip(
            'Start streaming data from the camera')
        self.sample_animation_btn.move(30 + 133 * 3, 620)
        self.sample_animation_btn.resize(100, 30)

        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(5, 1)
        self.layout.setRowMinimumHeight(0, 30)
        self.layout.addWidget(self.header, 0, 1, 2, 4, Qt.AlignTop)
        self.layout.addWidget(self.plot, 2, 1, 4, 4)
        self.layout.addWidget(self.toolbar, 6, 1, 2, 4)
        self.layout.addWidget(self.save_btn, 8, 3, 2, 1)
        self.layout.addWidget(self.sample_animation_btn, 8, 4, 2, 1)
        self.layout.setRowStretch(9, 1)

        self.show()

    def SaveStream(self):
        date = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        path = os.path.join(
            'helicam\logs', 'intensity_data_list_' + date + '.npy')
        self.scan.SaveScansArray(path)


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
        path = "helicam\intensity_img_2021_10_12-05_18_58_PM.npy"
        data = np.load(path)

        # Start by showing frame 0 and I parameter
        frameNum = 0
        IQProperty = 0
        self.data_to_graph = data[frameNum, :, :, IQProperty]

        # Initialize main plot
        self.main = self.fig.add_subplot(10, 10, (1, 10*8-2))
        self.graph = self.main.imshow(self.data_to_graph)

        # Init cursor annotation
        # self.cursor = matplotlib.widgets.Cursor(self.main, horizOn=True, vertOn=True, useblit=True,
        #                                         color='grey', linewidth=0.5, linestyle='dotted')
        self.target = [90, 150]
        self.y_target_line = self.main.axhline(
            y=self.target[0], color='black', linestyle='dotted', linewidth=0.5)
        self.x_target_line = self.main.axvline(
            x=self.target[1], color='black', linestyle='dotted', linewidth=0.5)

        # Calculate maximum value
        max_val = np.amax(self.data_to_graph)

        # Initialize column plot
        self.col_g = self.fig.add_subplot(10, 10, (10, 10*8), sharey=self.main)
        self.col_graph, = self.col_g.plot(
            self.data_to_graph[:, self.target[1]], np.arange(300))  # Display vertically
        self.col_g.set_ylim([300, 0])
        self.col_g.set_xlim([max_val + 100, 0])
        self.col_g.yaxis.set_visible(False)
        self.col_g.xaxis.set_visible(False)
        self.col_g.grid(False)

        # Turn off spines
        for key, spine in self.col_g.spines.items():
            spine.set_visible(False)

        # Initialize row plot
        self.row_g = self.fig.add_subplot(
            10, 10, (10*9+1, 10*10-2), sharex=self.main)
        self.row_graph, = self.row_g.plot(
            self.data_to_graph[self.target[0], :])
        self.row_g.set_ylim([0, max_val + 100])
        self.row_g.set_xlim([0, 300])
        self.row_g.yaxis.set_visible(False)
        self.row_g.xaxis.set_visible(False)

        # Turn off spines
        for key, spine in self.row_g.spines.items():
            spine.set_visible(False)

        # Record coordinates when user clicks on the plot
        self.fig.canvas.mpl_connect('button_press_event', self.OnClick)

        self.figure.tight_layout()
        self.draw()

    def OnClick(self, event):

        # Update row graph
        self.target[0] = int(event.ydata)
        self.row_graph.set_ydata(self.data_to_graph[self.target[0], :])

        # Update column graph
        self.target[1] = int(event.xdata)
        self.col_graph.set_xdata(self.data_to_graph[:, self.target[1]])

        # Update target lines
        self.UpdateTargetLines()

        self.draw()

    def RunSampleAnimation(self):
        if(self.parent.sample_animation_btn.isChecked() == True):

            def UpdateFig(*args):
                if (CAMERA_CONNECTED):
                    self.data_to_graph = self.parent.scan.GetIntensityMeasurement()
                else:
                    self.data_to_graph = np.rot90(self.data_to_graph)

                self.graph.set_array(self.data_to_graph)

                return self.graph, self.x_target_line, self.y_target_line,

            # Set animation
            self.animation = matplotlib.animation.FuncAnimation(
                self.fig, UpdateFig, interval=200, blit=True)

            self.draw()
        else:
            # Pause animation
            self.animation.pause()

    def UpdateTargetLines(self):
        self.y_target_line.set_ydata(self.target[0])
        self.x_target_line.set_xdata(self.target[1])

        self.draw()

    def UpdateGraphLimits(self):
        # Calculate maximum and minimum values
        max_val = np.amax(self.data_to_graph)
        min_val = np.amin(self.data_to_graph)

        self.col_g.set_xlim([max_val * 1.1, min_val * 1.1])
        self.row_g.set_ylim([min_val * 1.1, max_val * 1.1])
