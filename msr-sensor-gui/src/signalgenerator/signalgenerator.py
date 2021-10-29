from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class SignalGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.InitUI()

    def InitUI(self):
        # Tab header
        font = QFont()
        font.setPointSize(20)
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Signal Generator Settings")
        self.header.move(30, 20)

        # Pattern preview from matplotlib
        self.plot = PatternPlot(self, width=5, height=3)
        self.plot.move(30, 80)

        # Set shadow behind widget
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(1)
        shadow.setColor(QColor(20, 20, 20, 30))
        self.plot.setGraphicsEffect(shadow)

        # Set font for all small headers
        font = QFont()
        font.setPointSize(8)

        # Waveform type label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Waveform")
        self.header.move(30, 410)

        # Waveform type
        self.waveform = QComboBox(self)
        self.waveform.move(30, 430)
        self.waveform.resize(100, 30)
        # self.waveform.valueChanged.connect()

        # Amplitude label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Amplitude")
        self.header.move(30 + 133, 410)

        # Amplitude
        self.amplitude = QSpinBox(self)
        self.amplitude.move(30 + 133, 430)
        self.amplitude.resize(100, 30)
        self.amplitude.setRange(0, 10000)
        # self.amplitude.setValue()
        # self.amplitude.valueChanged.connect()

        # Offset label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Offset")
        self.header.move(30 + 133 * 2, 410)

        # Offset label
        self.offset = QSpinBox(self)
        self.offset.move(30 + 133 * 2, 430)
        self.offset.resize(100, 30)
        self.offset.setRange(-10000, 10000)
        # self.offset.setValue()
        # self.offset.valueChanged.connect()

        # Frequency label
        self.header = QLabel(self)
        self.header.setFont(font)
        self.header.setText("Frequency")
        self.header.move(30 + 133 * 3, 410)

        # Frequency label
        self.frequency = QSpinBox(self)
        self.frequency.move(30 + 133 * 3, 430)
        self.frequency.resize(100, 30)
        self.frequency.setRange(0, 10000)
        # self.frequency.setValue()
        # self.frequency.valueChanged.connect()

        # Send settings to signal generator
        self.set_signal = QPushButton('Set Signal', self)
        # self.set_signal.clicked.connect()
        self.set_signal.setToolTip('Send settings to signal generator')
        self.set_signal.move(30 + 133 * 3, 500)
        self.set_signal.resize(100, 30)

        self.show()


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

    def plot(self):
        # Initialize axes
        self.ax = self.figure.add_subplot(111)

        self.draw()
