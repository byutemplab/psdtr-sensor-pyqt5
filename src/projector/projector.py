import os
import usb.core
import usb.util

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot
import matplotlib.animation
import matplotlib.colors

from .dotspattern import DotsPattern
from .pycrafter6500 import dmd

RES_Y = 1920
RES_X = 1080

# Custom style for plot navigation toolbar


class PlotNavigation(NavigationToolbar):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Subplots')]


class ProjectorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.green_dots_pattern = DotsPattern()
        self.laser_dots_pattern = DotsPattern()

        # Set connection to projectors
        devices = list(usb.core.find(
            idVendor=0x0451, idProduct=0xc900, find_all=True))
        print("Found {} projector(s)".format(len(devices)))

        if(len(devices) == 0):
            print("No projector found")
            self.projector_1 = dmd()
            self.projector_2 = dmd()
        elif(len(devices) == 1):
            self.projector_1 = dmd(devices[0], devices[0].address)
            self.projector_2 = dmd()
        elif(len(devices) == 2):
            self.projector_1 = dmd(devices[0], devices[0].address)
            self.projector_2 = dmd(devices[1], devices[1].address)

        self.rgb_projector = self.projector_1
        self.laser_projector = self.projector_2

        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Projector Settings")
        self.header.setContentsMargins(0, 10, 0, 10)

        # Pattern preview from matplotlib
        self.plot = PatternPlot(self, width=5, height=3)
        self.plot.move(30, 80)

        # Navigation toolbar for graph
        self.toolbar = PlotNavigation(self.plot, self)
        self.toolbar.move(22, 400)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.plot.setGraphicsEffect(shadow)

        # Set font for all small headers
        font = QFont()
        font.setPointSize(8)

        # Number of measurements label
        self.header_measurements = QLabel(self)
        self.header_measurements.setFont(font)
        self.header_measurements.setText("# Measurements")
        self.header_measurements.move(30, 460)

        # Number of measurements
        self.num_measurements = QSpinBox(self)
        self.num_measurements.move(30, 480)
        self.num_measurements.resize(100, 30)
        self.num_measurements.setValue(
            self.green_dots_pattern.num_measurements)
        self.num_measurements.setRange(2, 50)
        self.num_measurements.valueChanged.connect(self.ChangeNumMeasurements)

        # Green Point diameter label
        self.header_green_diameter = QLabel(self)
        self.header_green_diameter.setFont(font)
        self.header_green_diameter.setText("Green Point Diameter")

        # Green Point diameter
        self.green_point_diameter = QSpinBox(self)
        self.green_point_diameter.setValue(
            self.green_dots_pattern.point_diameter)
        self.green_point_diameter.setRange(1, 100)
        self.green_point_diameter.valueChanged.connect(
            self.ChangeGreenPointDiameter)

        # Laser Point diameter label
        self.header_laser_diameter = QLabel(self)
        self.header_laser_diameter.setFont(font)
        self.header_laser_diameter.setText("Laser Point Diameter")

        # Laser Point diameter
        self.laser_point_diameter = QSpinBox(self)
        self.laser_point_diameter.setValue(
            self.laser_dots_pattern.point_diameter)
        self.laser_point_diameter.setRange(1, 100)
        self.laser_point_diameter.valueChanged.connect(
            self.ChangeLaserPointDiameter)

        # Exposure time label
        self.header_exposure = QLabel(self)
        self.header_exposure.setFont(font)
        self.header_exposure.setText("Exposure Time")
        self.header_exposure.move(30 + 133 * 2, 460)

        # Exposure time label
        self.exposure = QSpinBox(self)
        self.exposure.move(30 + 133 * 2, 480)
        self.exposure.resize(100, 30)
        self.exposure.setRange(0, 1000)
        self.exposure.setValue(self.green_dots_pattern.exposure)
        self.exposure.valueChanged.connect(self.ChangeExposure)

        # Preview button
        self.preview_btn = QPushButton('Preview', self)
        self.preview_btn.setCheckable(True)
        self.preview_btn.clicked.connect(self.plot.PreviewAnimation)
        self.preview_btn.setToolTip('Preview sequence animation')
        self.preview_btn.move(30 + 133 * 3, 480)
        self.preview_btn.resize(100, 30)

        # Trajectory selection label
        self.header_trajectory_selection = QLabel(self)
        self.header_trajectory_selection.setFont(font)
        self.header_trajectory_selection.setText("Pattern Array")
        self.header_trajectory_selection.move(30, 530)

        # Trajectory selection
        self.trajectory_selection = QComboBox(self)
        self.trajectory_selection.move(30, 550)
        self.trajectory_selection.resize(100, 30)
        self.trajectory_selection.activated[str].connect(
            self.ChangeTrajectorySelection)

        # New trajectory label
        self.header_new_trajectory = QLabel(self)
        self.header_new_trajectory.setFont(font)
        self.header_new_trajectory.setText("New Trajectory")
        self.header_new_trajectory.move(30 + 133, 530)

        # New trajectory button
        self.new_trajectory_btn = QPushButton('+', self)
        self.new_trajectory_btn.clicked.connect(self.AddNewTrajectory)
        self.new_trajectory_btn.setToolTip(
            'Add new trajectory to the array (N)')
        self.new_trajectory_btn.move(30 + 133, 550)
        self.new_trajectory_btn.resize(100, 30)

        # Select start point label
        self.header_start_point = QLabel(self)
        self.header_start_point.setFont(font)
        self.header_start_point.setText("Starting Point")
        self.header_start_point.move(30 + 133 * 2, 530)

        # Select start point
        self.start_point_btn = QPushButton('Select', self)
        self.start_point_btn.setCheckable(True)
        self.start_point_btn.clicked.connect(self.ClickedStartPointBtn)
        self.start_point_btn.setToolTip(
            'Select start point for the trajectory (S)')
        self.start_point_btn.move(30 + 133 * 2, 550)
        self.start_point_btn.resize(100, 30)

        # Select end point label
        self.header_end_point = QLabel(self)
        self.header_end_point.setFont(font)
        self.header_end_point.setText("Ending Point")
        self.header_end_point.move(30 + 133 * 3, 530)

        # Select end point
        self.end_point_btn = QPushButton('Select', self)
        self.end_point_btn.setCheckable(True)
        self.end_point_btn.clicked.connect(self.ClickedEndPointBtn)
        self.end_point_btn.setToolTip(
            'Select end point for the trajectory (E)')
        self.end_point_btn.move(30 + 133 * 3, 550)
        self.end_point_btn.resize(100, 30)

        # Switch connection of projectors
        self.switch_btn = QPushButton('Switch projectors', self)
        self.switch_btn.clicked.connect(self.Switch)
        self.switch_btn.setToolTip(
            'Switch connection of laser and rgb projectors')

        # Send pattern to projector
        self.send_pattern_btn = QPushButton('Send Pattern', self)
        self.send_pattern_btn.clicked.connect(self.SendPattern)
        self.send_pattern_btn.setToolTip('Send pattern to projector')

        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(5, 1)
        self.layout.setRowMinimumHeight(0, 30)
        self.layout.addWidget(self.header, 0, 1, 2, 4, Qt.AlignTop)
        self.layout.addWidget(self.plot, 2, 1, 2, 4)
        self.layout.addWidget(self.toolbar, 4, 1, 2, 3)
        self.layout.addWidget(self.header_measurements, 6, 1)
        self.layout.addWidget(self.num_measurements, 7, 1)
        self.layout.addWidget(self.header_green_diameter, 6, 2)
        self.layout.addWidget(self.green_point_diameter, 7, 2)
        self.layout.addWidget(self.header_laser_diameter, 6, 3)
        self.layout.addWidget(self.laser_point_diameter, 7, 3)
        self.layout.addWidget(self.header_exposure, 6, 4)
        self.layout.addWidget(self.exposure, 7, 4)
        self.layout.addWidget(self.preview_btn, 4, 4, 2, 1)
        self.layout.addWidget(self.header_trajectory_selection, 8, 1)
        self.layout.addWidget(self.trajectory_selection, 9, 1)
        self.layout.addWidget(self.header_new_trajectory, 8, 2)
        self.layout.addWidget(self.new_trajectory_btn, 9, 2)
        self.layout.addWidget(self.header_start_point, 8, 3)
        self.layout.addWidget(self.start_point_btn, 9, 3)
        self.layout.addWidget(self.header_end_point, 8, 4)
        self.layout.addWidget(self.end_point_btn, 9, 4)
        self.layout.addWidget(self.switch_btn, 10, 3, 2, 1)
        self.layout.addWidget(self.send_pattern_btn, 10, 4, 2, 1)
        self.layout.setRowStretch(11, 1)

        self.show()

    def ClickedStartPointBtn(self):
        if(self.end_point_btn.isChecked()):
            self.end_point_btn.toggle()

    def ClickedEndPointBtn(self):
        if(self.start_point_btn.isChecked()):
            self.start_point_btn.toggle()

    def ChangeNumMeasurements(self, value):
        self.green_dots_pattern.num_measurements = value

    def ChangeGreenPointDiameter(self, value):
        self.green_dots_pattern.point_diameter = value

    def ChangeLaserPointDiameter(self, value):
        self.laser_dots_pattern.point_diameter = value

    def ChangeExposure(self, value):
        self.green_dots_pattern.exposure = value
        self.laser_dots_pattern.exposure = value

    def ChangeTrajectorySelection(self, value):
        # Get index of selected trajectory
        self.plot.selected_trajectory_idx = int(value.split(" ")[1]) - 1

    def AddNewTrajectory(self):
        self.plot.trajectories_list.append({'start': (0, 0), 'end': (0, 0)})
        num_trajectory = len(self.plot.trajectories_list)
        newItem = "Trajectory " + str(num_trajectory)
        self.trajectory_selection.addItem(newItem)
        self.trajectory_selection.setCurrentText(newItem)
        self.plot.selected_trajectory_idx = num_trajectory - 1  # Conversion to 0-index

        # Toggle on starting point selection button
        if(self.start_point_btn.isChecked() == False):
            self.start_point_btn.toggle()

    def Switch(self):
        if (self.rgb_projector == self.projector_1):
            self.rgb_projector = self.projector_2
            self.laser_projector = self.projector_1
        else:
            self.rgb_projector = self.projector_1
            self.laser_projector = self.projector_2

    def SendPattern(self):
        print('Sending pattern to projector')
        self.plot.UpdateFrames()
        self.green_dots_pattern.Send(self.rgb_projector)
        self.laser_dots_pattern.Send(self.laser_projector)

    def keyPressEvent(self, event):
        key = event.key()
        # On N key press, add new trajectory
        if key == Qt.Key_N:
            self.AddNewTrajectory()

        # On S key press, toggle start point button
        if key == Qt.Key_S:
            self.start_point_btn.toggle()

        # On E key press, toggle end point button
        if key == Qt.Key_E:
            self.end_point_btn.toggle()

    def Enable(self, enable):
        self.num_measurements.setEnabled(enable)
        self.green_point_diameter.setEnabled(enable)
        self.laser_point_diameter.setEnabled(enable)
        self.exposure.setEnabled(enable)
        self.trajectory_selection.setEnabled(enable)
        self.new_trajectory_btn.setEnabled(enable)
        self.start_point_btn.setEnabled(enable)
        self.end_point_btn.setEnabled(enable)


class PatternPlot(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.parent = parent
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.plot()

        # delete
        self.test = 0

    def plot(self):
        # Set initial parameters
        self.trajectories_list = []
        self.selected_trajectory_idx = 0
        self.annotations_list = []

        # Initialize axes
        self.ax = self.figure.add_subplot(111)

        # Import grain boundary sample image and set as background
        # Resize to projector resolution (1920x1080)
        print(os.getcwd())
        self.image = matplotlib.pyplot.imread(
            "projector/grain-boundaries/sample.png")
        self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])

        # Record coordinates when user clicks on the plot
        self.fig.canvas.mpl_connect('button_press_event', self.OnClick)

        self.figure.tight_layout()
        self.draw()

    def UpdateFrames(self):
        self.parent.green_dots_pattern.UpdatePattern(
            self.trajectories_list, 'rgb')
        self.parent.laser_dots_pattern.UpdatePattern(
            self.trajectories_list, 'laser')

    def PreviewAnimation(self):
        if(self.parent.preview_btn.isChecked() == True):
            # Disable controls
            self.parent.Enable(False)

            self.UpdateFrames()
            self.RemoveTrajectories()

            # Custom binary colormap dependant on point_color selection
            cmap_green = matplotlib.colors.ListedColormap(['none', '#00ff00'])
            cmap_laser = matplotlib.colors.ListedColormap(['none', '#ff0000'])

            # Start with first frame
            self.graph_green = self.ax.imshow(
                self.parent.green_dots_pattern.frames_array[0], cmap=cmap_green)
            self.graph_laser = self.ax.imshow(
                self.parent.laser_dots_pattern.frames_array[0], cmap=cmap_laser)

            # Superpose background to hide initial frame
            self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])

            # Update graph with next frame
            self.frame_num = 0

            def UpdateFig(*args):
                self.graph_green.set_array(
                    self.parent.green_dots_pattern.frames_array[self.frame_num % self.parent.green_dots_pattern.num_measurements])
                self.graph_laser.set_array(
                    self.parent.laser_dots_pattern.frames_array[self.frame_num % self.parent.laser_dots_pattern.num_measurements])
                self.frame_num += 1
                return self.graph_green, self.graph_laser

            # Set animation
            self.animation = matplotlib.animation.FuncAnimation(
                self.fig, UpdateFig, interval=self.parent.green_dots_pattern.exposure, blit=True)

            self.draw()
        else:
            # Re-enable controls
            self.parent.Enable(True)

            try:
                # Pause animation
                self.animation.pause()

                # Superpose background to hide initial frame and show trajectories again
                self.ax.imshow(self.image, extent=[0, RES_Y, RES_X, 0])
                self.ShowTrajectories()
            except:
                print("No animation yet")

    def OnClick(self, event):
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
