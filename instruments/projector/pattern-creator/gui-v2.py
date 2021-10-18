import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.colors

import skimage.draw
import numpy as np

import pycrafter6500

RES_Y = 1920
RES_X = 1080


def CreateDotsPatternArray(trajectories_list, num_frames, point_diameter=5, rows=RES_Y, columns=RES_X):
    # Init empty array
    frames_array = []
    for frame in range(num_frames):
        frames_array.append(np.zeros((columns, rows)).astype(np.uint8))

    # Draw each green dot trajectory in the frames array
    for trajectory in trajectories_list:
        # Get every point in the line
        rr, cc = skimage.draw.line(trajectory['start'][0], trajectory['start'][1],
                                   trajectory['end'][0], trajectory['end'][1])

        # Calculate distance between dots
        dot_step = (len(rr) - 1) / (num_frames - 1)

        # Go through each frame, draw corresponding points
        for frame_idx, frame in enumerate(frames_array):
            # Get point in the line for this frame
            dot_idx = round(frame_idx * dot_step)

            # Draw point in current frame
            try:
                rr_disk, cc_disk = skimage.draw.disk(
                    (rr[dot_idx], cc[dot_idx]), point_diameter)
                frame[rr_disk, cc_disk] = 1
            except:
                out_of_bounds = True

    return frames_array


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


class TabBar(QTabBar):
    def tabSizeHint(self, index):
        s = QTabBar.tabSizeHint(self, index)
        s.transpose()
        return s

    def paintEvent(self, event):
        painter = QStylePainter(self)
        opt = QStyleOptionTab()

        for i in range(self.count()):
            self.initStyleOption(opt, i)
            painter.drawControl(QStyle.CE_TabBarTabShape, opt)
            painter.save()

            s = opt.rect.size()
            s.transpose()
            r = QRect(QPoint(), s)
            r.moveCenter(opt.rect.center())
            opt.rect = r

            c = self.tabRect(i).center()
            painter.translate(c)
            painter.rotate(90)
            painter.translate(-c)
            painter.drawControl(QStyle.CE_TabBarTabLabel, opt)
            painter.restore()


class CustomTabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        self.setTabPosition(QTabWidget.West)


class ProxyStyle(QProxyStyle):
    def drawControl(self, element, opt, painter, widget):
        if element == QStyle.CE_TabBarTabLabel:
            ic = self.pixelMetric(QStyle.PM_TabBarIconSize)
            r = QRect(opt.rect)
            w = 0 if opt.icon.isNull() else opt.rect.width() + \
                self.pixelMetric(QStyle.PM_TabBarIconSize)
            r.setHeight(opt.fontMetrics.width(opt.text) + w)
            r.moveBottom(opt.rect.bottom())
            opt.rect = r
        QProxyStyle.drawControl(self, element, opt, painter, widget)


class camera_tab(QWidget):
    def __init__(self):
        super().__init__()
        self.header = QLabel(self)
        self.header.setText("Hello World")


class App(CustomTabWidget):

    def __init__(self):
        super().__init__()
        self.left = 340
        self.top = 40
        self.title = 'TEMPLAB MSR Sensor'
        self.width = 700
        self.height = 680
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('icons/msr-sensor-icon.png'))
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.projector_tab = QWidget()
        self.camera_tab = QWidget()
        self.addTab(self.projector_tab, QIcon(
            "icons/projector-icon.png"), "DMD Projector")

        camera_widget = camera_tab()
        self.addTab(camera_widget, QIcon(
            "icons/camera-icon.png"), "  Heliotis Camera")

        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.projector_tab.header = QLabel(self)
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
        font = QFont()
        font.setPointSize(8)

        # Number of measurements label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("# Measurements")
        self.header.move(160, 410)

        # Number of measurements
        self.num_measurements = QSpinBox(self)
        self.num_measurements.move(160, 430)
        self.num_measurements.resize(100, 30)
        self.num_measurements.setValue(self.m.num_measurements)
        self.num_measurements.setRange(2, 50)
        self.num_measurements.valueChanged.connect(self.ChangeNumMeasurements)

        # Point diameter label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Point Diameter")
        self.header.move(160 + 133, 410)

        # Point diameter
        self.point_diameter = QSpinBox(self)
        self.point_diameter.move(160 + 133, 430)
        self.point_diameter.resize(100, 30)
        self.point_diameter.setValue(self.m.point_diameter)
        self.point_diameter.setRange(1, 100)
        self.point_diameter.valueChanged.connect(self.ChangePointDiameter)

        # Exposure time label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Exposure Time")
        self.header.move(160 + 133 * 2, 410)

        # Exposure time label
        self.exposure = QSpinBox(self)
        self.exposure.move(160 + 133 * 2, 430)
        self.exposure.resize(100, 30)
        self.exposure.setRange(0, 1000)
        self.exposure.setValue(self.m.exposure)
        self.exposure.valueChanged.connect(self.ChangeExposure)

        # Preview button
        self.preview_btn = QPushButton('Preview', self)
        self.preview_btn.setCheckable(True)
        self.preview_btn.clicked.connect(self.m.PreviewAnimation)
        self.preview_btn.setToolTip('Preview sequence animation')
        self.preview_btn.move(160 + 133 * 3, 430)
        self.preview_btn.resize(100, 30)

        # Trajectory selection label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Pattern Array")
        self.header.move(160, 480)

        # Trajectory selection
        self.trajectory_selection = QComboBox(self)
        self.trajectory_selection.move(160, 500)
        self.trajectory_selection.resize(100, 30)
        self.trajectory_selection.activated[str].connect(
            self.ChangeTrajectorySelection)

        # New trajectory label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("New Trajectory")
        self.header.move(160 + 133, 480)

        # New trajectory button
        self.new_trajectory_btn = QPushButton('+', self)
        self.new_trajectory_btn.clicked.connect(self.AddNewTrajectory)
        self.new_trajectory_btn.setToolTip(
            'Add new trajectory to the array (N)')
        self.new_trajectory_btn.move(160 + 133, 500)
        self.new_trajectory_btn.resize(100, 30)

        # Select start point label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Starting Point")
        self.header.move(160 + 133 * 2, 480)

        # Select start point
        self.start_point_btn = QPushButton('Select', self)
        self.start_point_btn.setCheckable(True)
        self.start_point_btn.clicked.connect(self.ClickedStartPointBtn)
        self.start_point_btn.setToolTip(
            'Select start point for the trajectory (S)')
        self.start_point_btn.move(160 + 133 * 2, 500)
        self.start_point_btn.resize(100, 30)

        # Select end point label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Ending Point")
        self.header.move(160 + 133 * 3, 480)

        # Select end point
        self.end_point_btn = QPushButton('Select', self)
        self.end_point_btn.setCheckable(True)
        self.end_point_btn.clicked.connect(self.ClickedEndPointBtn)
        self.end_point_btn.setToolTip(
            'Select end point for the trajectory (E)')
        self.end_point_btn.move(160 + 133 * 3, 500)
        self.end_point_btn.resize(100, 30)

        # Connection Status
        self.connection_status = QLabel(self)
        self.connection_status.setFont(font)
        self.connection_status.setText("Disconnected")
        self.connection_status.move(160 + 133 * 2 + 30, 577)

        # Check connection status every 2 seconds
        self.check_connection_timer = QTimer(self)
        self.check_connection_timer.setInterval(2000)  # 2 seconds
        self.check_connection_timer.timeout.connect(lambda: print("hey"))

        # Send pattern to projector
        self.send_pattern_btn = QPushButton('Send Pattern', self)
        self.send_pattern_btn.clicked.connect(self.SendPattern)
        self.send_pattern_btn.setToolTip('Send pattern to projector')
        self.send_pattern_btn.move(160 + 133 * 3, 570)
        self.send_pattern_btn.resize(100, 30)

        self.show()

    def ClickedStartPointBtn(self):
        if(self.end_point_btn.isChecked()):
            self.end_point_btn.toggle()

    def ClickedEndPointBtn(self):
        if(self.start_point_btn.isChecked()):
            self.start_point_btn.toggle()

    def ChangeNumMeasurements(self, value):
        self.m.num_measurements = value

    def ChangePointDiameter(self, value):
        self.m.point_diameter = value

    def ChangeExposure(self, value):
        self.m.exposure = value

    def ChangeTrajectorySelection(self, value):
        # Get index of selected trajectory
        self.m.selected_trajectory_idx = int(value.split(" ")[1]) - 1

    def AddNewTrajectory(self):
        self.m.trajectories_list.append({'start': (0, 0), 'end': (0, 0)})
        num_trajectory = len(self.m.trajectories_list)
        newItem = "Trajectory " + str(num_trajectory)
        self.trajectory_selection.addItem(newItem)
        self.trajectory_selection.setCurrentText(newItem)
        self.m.selected_trajectory_idx = num_trajectory - 1  # Conversion to 0-index

        # Toggle on starting point selection button
        if(self.start_point_btn.isChecked() == False):
            self.start_point_btn.toggle()

    def SendPattern(self):
        print('Sending pattern to projector')
        self.m.UpdateFrames()
        SetPatternSequence(self.m.frames_array, 'green',
                           self.m.exposure * 1000)

    def keyPressEvent(self, event):
        key = event.key()
        # On N key press, add new trajectory
<<<<<<< HEAD
        if key == Qt.Key_N:
            self.AddNewTrajectory()

        # On S key press, toggle start point button
        if key == Qt.Key_S:
            self.start_point_btn.toggle()

        # On E key press, toggle end point button
        if key == Qt.Key_E:
=======
        if key == QtCore.Qt.Key_N:
            self.AddNewTrajectory()

        # On S key press, toggle start point button
        if key == QtCore.Qt.Key_S:
            self.start_point_btn.toggle()

        # On E key press, toggle end point button
        if key == QtCore.Qt.Key_E:
>>>>>>> 49957849b96a7378c0dbc68f7e96dd932dfd4651
            self.end_point_btn.toggle()

    def CheckConnection(self):
        # If not connected, try to connect
        # if (dlp.connected == False):
        #     dlp.TryConnection()
        print("yo, whats up")


class PlotCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.parent = parent
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvasQTAgg.setSizePolicy(self,
                                        QSizePolicy.Expanding,
                                        QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
        self.plot()

    def plot(self):
        # Set initial parameters
        self.num_measurements = 10
        self.point_diameter = 20
        self.exposure = 50  # in milliseconds
        self.frames_array = []
        self.trajectories_list = []
        self.selected_trajectory_idx = 0
        self.annotations_list = []

        # Initialize axes
        self.ax = self.figure.add_subplot(111)

        # Import grain boundary sample image and set as background
        # Resize to projector resolution (1920x1080)
        self.image = matplotlib.pyplot.imread("grain-boundaries/sample.png")
        self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])

        # Record coordinates when user clicks on the plot
        self.fig.canvas.mpl_connect('button_press_event', self.onClick)

        self.draw()

    def UpdateFrames(self):
        self.frames_array = CreateDotsPatternArray(self.trajectories_list,
                                                   self.num_measurements,
                                                   self.point_diameter)

    def PreviewAnimation(self, value):
        if(self.parent.preview_btn.isChecked() == True):
            self.UpdateFrames()
            self.RemoveTrajectories()

            # Custom binary colormap dependant on point_color selection
            cmap = matplotlib.colors.ListedColormap(['none', '#00ff00'])

            # Start with first frame
            self.graph = self.ax.imshow(self.frames_array[0], cmap=cmap)

            # Superpose background to hide initial frame
            self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])

            # Update graph with next frame
            self.frame_num = 0

            def UpdateFig(*args):
                self.graph.set_array(
                    self.frames_array[self.frame_num % self.num_measurements])
                self.frame_num += 1
                return self.graph,

            # Set animation
<<<<<<< HEAD
            self.animation = matplotlib.animation.FuncAnimation(
=======
            self.animation = animation.FuncAnimation(
>>>>>>> 49957849b96a7378c0dbc68f7e96dd932dfd4651
                self.fig, UpdateFig, interval=self.exposure, blit=True)

            self.draw()
        else:
            try:
                # Pause animation
                self.animation.pause()

                # Superpose background to hide initial frame and show trajectories again
                self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])
                self.ShowTrajectories()
            except:
                print("no animation yet")

    def onClick(self, event):
        if (self.parent.start_point_btn.isChecked()):
            # Set starting point for trajectory
            coord = (int(event.ydata), int(event.xdata))
            self.trajectories_list[self.selected_trajectory_idx]['start'] = coord

            # Toggle button back off
            self.parent.start_point_btn.toggle()

            # If end point was not set already, set to same coords as start point and toggle on end point selection
            if(self.trajectories_list[self.selected_trajectory_idx]['end'] == (0, 0)):
                self.trajectories_list[self.selected_trajectory_idx]['end'] = coord
                self.parent.end_point_btn.toggle()

        elif (self.parent.end_point_btn.isChecked()):
            # Set ending point for trajectory
            coord = (int(event.ydata), int(event.xdata))
            self.trajectories_list[self.selected_trajectory_idx]['end'] = coord

            # If start point was not set already, set to same coords as end point
            if(self.trajectories_list[self.selected_trajectory_idx]['start'] == (0, 0)):
                self.trajectories_list[self.selected_trajectory_idx]['start'] = coord

            # Toggle button back off
            self.parent.end_point_btn.toggle()

        # Show in terminal
        print(self.trajectories_list)

        # Show in graph
        self.ShowTrajectories()

    def ShowTrajectories(self):
        self.RemoveTrajectories()
        for idx, trajectory in enumerate(self.trajectories_list):
            name = "T" + str(idx + 1)
            a = self.ax.annotate(name, xy=(trajectory['end'][1], trajectory['end'][0]), xytext=(trajectory['start'][1], trajectory['start'][0]),
                                 arrowprops=dict(arrowstyle="-|>", lw=1.5))
            self.annotations_list.append(a)

        self.draw()

    def RemoveTrajectories(self):
        for annotation in self.annotations_list:
            annotation.remove()
        self.annotations_list = []


if __name__ == '__main__':

    # Inititalize dmd
    dlp = pycrafter6500.dmd()

    # Start GUI
    app = QApplication(sys.argv)
    QApplication.setStyle(ProxyStyle())
    app.setStyle("Fusion")
    ex = App()
    sys.exit(app.exec_())
