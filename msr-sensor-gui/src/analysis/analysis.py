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
        path = "camera\logs\sequence_sample_1.npy"
        self.scan_array = (1 * (np.load(path) < 0)).astype('uint8')

        # Start by showing frame 0 and I parameter\
        self.data_to_graph = self.scan_array[0]

        # Initialize main plot
        self.main = self.fig.add_subplot()
        self.main_graph = self.main.imshow(self.data_to_graph)

        # Find biggest blub and draw a contour box
        x, y, w, h = self.FindBiggestBlob(self.data_to_graph)
        self.contour_box = self.main.add_patch(
            matplotlib.patches.Rectangle((x, y), w, h, fill=False, color='g'))

        # Show value when user clicks
        self.fig.canvas.mpl_connect('button_press_event', self.OnClick)

        self.draw()

    def OnClick(self, event):
        x = int(event.xdata)
        y = int(event.ydata)
        value = self.data_to_graph[y, x]
        print(value)

    def RunSampleAnimation(self):
        if(self.parent.sample_animation_btn.isChecked() == True):

            self.cnt = 0

            def UpdateFig(*args):
                self.cnt += 1

                # Update array frame
                frame = self.cnt % self.scan_array.shape[0]
                self.data_to_graph = self.scan_array[frame]
                self.main_graph.set_array(self.data_to_graph)

                # Update blob position
                x, y, w, h = self.FindBiggestBlob(self.data_to_graph)
                self.contour_box.set_bounds(x, y, w, h)

                return self.main_graph, self.contour_box,

            # Set animation
            self.animation = matplotlib.animation.FuncAnimation(
                self.fig, UpdateFig, interval=200, blit=True)

            self.draw()
        else:
            # Pause animation
            self.animation.pause()

    def FindBiggestBlob(self, image):
        # Get all contours
        contours, hierarchy = cv2.findContours(
            image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Find largest contour
        c = max(contours, key=cv2.contourArea)

        # Return coordinates
        return cv2.boundingRect(c)
